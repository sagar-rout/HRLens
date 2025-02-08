from typing import Dict, Any, Optional
from pymilvus import Collection, connections, utility, FieldSchema, CollectionSchema, DataType
import numpy as np
from app.utils.logger import logger
from app.core.cache_stats import CacheStats
import json
from datetime import datetime


class VectorCache:
    _instance = None
    _initialized = False

    def __new__(cls, config: Dict[str, Any], es_client):
        if cls._instance is None:
            cls._instance = super(VectorCache, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: Dict[str, Any], es_client):
        if self._initialized:
            return

        # Core settings
        self.collection_name = "semantic_cache"
        self.collection = None
        # More restrictive threshold (0.2 means 80% similarity required)
        self.distance_threshold = 0.2
        self.stats = CacheStats.get_instance(es_client)

        try:
            # Initialize Milvus connection
            connections.connect(
                alias="default",
                host=config["milvus_host"],
                port=config["milvus_port"]
            )
            self._init_collection()
            logger.info(f"Vector cache initialized: {self.collection_name}")
            self._initialized = True
        except Exception as e:
            logger.error(f"Cache initialization failed: {str(e)}")

    def _init_collection(self):
        """Initialize or create the cache collection if it doesn't exist"""
        try:
            # Use existing collection if available
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
                count = self.collection.num_entities
                logger.info(f"Loaded existing cache with {count} entries")
                return

            # Create new collection
            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="query_vector", dtype=DataType.FLOAT_VECTOR, dim=1536),
                FieldSchema(name="query_text", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="es_query", dtype=DataType.VARCHAR, max_length=4000),
                FieldSchema(name="created_at", dtype=DataType.INT64)
            ]

            schema = CollectionSchema(fields=fields, description="Semantic query cache")
            self.collection = Collection(name=self.collection_name, schema=schema)

            # Create search index
            self.collection.create_index(
                field_name="query_vector",
                index_params={
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128}
                }
            )
            self.collection.load()
            logger.info("Created new cache collection")

        except Exception as e:
            logger.error(f"Collection initialization failed: {str(e)}", exc_info=True)
            raise

    def _format_vector(self, embedding: list) -> list:
        """Format embedding for Milvus float vector"""
        try:
            # Step 1: Convert to numpy array if not already
            if not isinstance(embedding, np.ndarray):
                embedding = np.array(embedding)
            logger.debug(f"Step 1 - Array shape: {embedding.shape}")

            # Step 2: Ensure we have a flat array
            embedding = embedding.ravel()
            logger.debug(f"Step 2 - Flattened shape: {embedding.shape}")

            # Step 3: Verify dimension
            if embedding.shape[0] != 1536:
                raise ValueError(f"Expected 1536 dimensions, got {embedding.shape[0]}")

            # Step 4: Convert to float32 and ensure contiguous
            embedding = np.ascontiguousarray(embedding, dtype=np.float32)

            # Step 5: Convert to Python float list
            vector = [float(x) for x in embedding]
            logger.debug(f"Step 5 - Final vector length: {len(vector)}")

            return vector

        except Exception as e:
            logger.error(f"Vector formatting failed: {str(e)}", exc_info=True)
            raise

    async def find_query(self, query: str, embedding: list) -> Optional[Dict]:
        """Find semantically similar query in cache"""
        if not self.collection:
            self.stats.update(hit=False, query=query, is_store=False)
            return None

        try:
            search_vector = self._format_vector(embedding)

            # Search with L2 distance and get top 3 matches
            results = self.collection.search(
                data=[search_vector],
                anns_field="query_vector",
                param={
                    "metric_type": "L2",
                    "params": {"nprobe": 16}  # Increased for better accuracy
                },
                limit=3,  # Get top 3 to find best match
                output_fields=["query_text", "es_query", "created_at"]
            )

            if not results or not results[0]:
                logger.debug("No results found in cache")
                self.stats.update(hit=False, query=query, is_store=False)
                return None

            # Find best match among top results
            best_match = None
            best_distance = float('inf')

            for hits in results[0]:
                distance = hits.distance
                # Normalize distance to 0-1 range
                similarity = 1 - (distance / 2)  # L2 distance normalized

                logger.debug(f"Candidate match: '{hits.entity.get('query_text')}' "
                             f"(similarity: {similarity:.4f})")

                if distance < self.distance_threshold and distance < best_distance:
                    best_match = hits
                    best_distance = distance

            if best_match:
                self.stats.update(hit=True, query=query, is_store=False)
                similarity = 1 - (best_distance / 2)
                logger.info(
                    f"Cache hit: '{query}' matched '{best_match.entity.get('query_text')}' "
                    f"(similarity: {similarity:.2%})"
                )
                return json.loads(best_match.entity.get('es_query'))

            logger.info(f"Cache miss - no matches above threshold ({self.distance_threshold})")
            self.stats.update(hit=False, query=query, is_store=False)
            return None

        except Exception as e:
            logger.error(f"Cache lookup failed: {str(e)}")
            self.stats.update(hit=False, query=query, is_store=False)
            return None

    async def store_query(self, query: str, embedding: list, es_query: Dict):
        """Store query in cache"""
        if not self.collection:
            return

        try:
            vector = self._format_vector(embedding)

            # Store with timestamp
            entity = {
                "query_vector": vector,
                "query_text": query,
                "es_query": json.dumps(es_query),
                "created_at": int(datetime.now().timestamp())
            }

            self.collection.insert([entity])
            self.collection.flush()

            # Update stats with store=True to increment queries_cached
            self.stats.update(hit=True, query=query, is_store=True)
            logger.info(f"Query cached: '{query}'")

        except Exception as e:
            logger.error(f"Failed to cache query: {str(e)}")
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics from Elasticsearch"""
        return self.stats.get_stats(
            total_entries=self.collection.num_entities if self.collection else 0
        )
