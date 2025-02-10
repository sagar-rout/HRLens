from typing import Dict, Any, Optional
from pymilvus import (
    Collection,
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
)
import numpy as np
import json
from app.utils.logger import logger
from datetime import datetime

class VectorCache:
    _instance = None
    _initialized = False

    def __new__(cls, config: Dict[str, Any] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize vector cache with Milvus configuration"""
        # Skip initialization if already initialized
        if VectorCache._initialized:
            return
            
        if config is None:
            raise ValueError("Config is required for first initialization")

        self.collection_name = "semantic_cache"
        self.collection = None
        self.similarity_threshold = 0.85  # Threshold for cache hits
        self.update_threshold = 0.95  # Threshold for updating existing entries
        self.milvus_config = config
        
        # Cache metrics
        self.total_hits = 0
        self.total_misses = 0
        self.last_hit = None
        self.last_miss = None
        self.last_stored = None

    async def initialize(self):
        """Initialize Milvus connection and collection"""
        if VectorCache._initialized:
            return

        try:
            connections.connect(
                alias="default",
                host=self.milvus_config["host"],
                port=self.milvus_config["port"]
            )
            await self._init_collection()
            VectorCache._initialized = True
            logger.info(f"Vector cache initialized: {self.collection_name}")
        except Exception as e:
            logger.error(f"Cache initialization failed: {str(e)}")
            raise

    async def _init_collection(self):
        """Initialize or create the cache collection"""
        try:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
                logger.info(f"Loaded existing cache with {self.collection.num_entities} entries")
                return

            fields = [
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name="query_vector", dtype=DataType.FLOAT_VECTOR, dim=768),
                FieldSchema(name="query_text", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="es_query", dtype=DataType.VARCHAR, max_length=4000),
                FieldSchema(name="created_at", dtype=DataType.INT64),
            ]

            schema = CollectionSchema(fields=fields, description="Semantic query cache")
            self.collection = Collection(name=self.collection_name, schema=schema)
            
            # Use HNSW index for better accuracy
            self.collection.create_index(
                field_name="query_vector",
                index_params={
                    "metric_type": "COSINE",
                    "index_type": "HNSW",
                    "params": {
                        "M": 16,
                        "efConstruction": 200
                    }
                }
            )
            self.collection.load()
            logger.info("Created new cache collection")

        except Exception as e:
            logger.error(f"Collection initialization failed: {str(e)}")
            raise

    async def find_query(self, query: str, embedding: list) -> Optional[Dict]:
        """Find semantically similar query in cache"""
        if not self.collection:
            self._record_miss(query)
            return None

        try:
            search_vector = np.array(embedding, dtype=np.float32).flatten().tolist()

            # Search with stricter parameters
            results = self.collection.search(
                data=[search_vector],
                anns_field="query_vector",
                param={
                    "metric_type": "L2",
                    "params": {
                        "nprobe": 32,  # Increased for better accuracy
                        "ef": 64       # Search scope
                    }
                },
                limit=1,
                output_fields=["query_text", "es_query"]
            )

            if not results or not results[0]:
                self._record_miss(query)
                return None

            hit = results[0][0]
            similarity = 1 - (hit.distance / 2)  # Convert L2 distance to similarity

            if similarity >= self.similarity_threshold:
                self._record_hit(query, hit.entity.get("query_text"), similarity)
                return json.loads(hit.entity.get("es_query"))

            self._record_miss(query, hit.entity.get("query_text"), similarity)
            return None

        except Exception as e:
            logger.error(f"Cache lookup failed: {str(e)}")
            self._record_miss(query)
            return None

    async def store_query(self, query: str, embedding: list, es_query: Dict):
        """Store query in cache"""
        if not self.collection:
            return

        try:
            vector = np.array(embedding, dtype=np.float32).flatten().tolist()
            
            # Check for very similar existing queries
            existing_results = self.collection.search(
                data=[vector],
                anns_field="query_vector",
                param={
                    "metric_type": "L2",
                    "params": {"nprobe": 32, "ef": 64}
                },
                limit=1,
                output_fields=["query_text", "id"]
            )

            # Only update if extremely similar
            similarity = 1 - (existing_results[0][0].distance / 2) if existing_results and existing_results[0] else 0
            if similarity >= self.update_threshold:
                hit = existing_results[0][0]
                expr = f"id == {hit.id}"
                self.collection.delete(expr)
                self.collection.flush()
                logger.info(f"Updated existing cache entry (similarity: {similarity:.2%}) for query: '{query}'")
            
            # Store new entry
            entity = {
                "query_vector": vector,
                "query_text": query,
                "es_query": json.dumps(es_query),
                "created_at": int(datetime.now().timestamp())
            }

            self.collection.insert([entity])
            self.collection.flush()
            
            self.last_stored = {
                "query": query,
                "time": datetime.now().isoformat(),
                "action": "updated" if similarity >= self.update_threshold else "inserted",
                "similarity": f"{similarity:.2%}" if similarity > 0 else None
            }
            
            logger.info(f"Query cached: '{query}' (action: {self.last_stored['action']})")

        except Exception as e:
            logger.error(f"Failed to cache query: {str(e)}")
            raise

    def _record_hit(self, query: str, matched_query: str, similarity: float):
        """Record cache hit with details"""
        self.total_hits += 1
        self.last_hit = {
            "query": query,
            "matched_query": matched_query,
            "similarity": f"{similarity:.2%}",
            "time": datetime.now().isoformat()
        }

    def _record_miss(self, query: str, best_match: str = None, similarity: float = None):
        """Record cache miss with details"""
        self.total_misses += 1
        miss_data = {
            "query": query,
            "time": datetime.now().isoformat()
        }
        if best_match and similarity:
            miss_data["best_match"] = {
                "query": best_match,
                "similarity": f"{similarity:.2%}"
            }
        self.last_miss = miss_data

    async def get_stats(self) -> Dict[str, Any]:
        """Get detailed cache statistics"""
        try:
            total_queries = self.total_hits + self.total_misses
            hit_rate = (self.total_hits / total_queries * 100) if total_queries > 0 else 0
            
            return {
                "cache_size": {
                    "total_entries": self.collection.num_entities if self.collection else 0,
                    "dimension": 768,
                    "collection_name": self.collection_name
                },
                "performance": {
                    "total_queries": total_queries,
                    "cache_hits": self.total_hits,
                    "cache_misses": self.total_misses,
                    "hit_rate": f"{hit_rate:.2f}%"
                },
                "recent_activity": {
                    "last_hit": self.last_hit,
                    "last_miss": self.last_miss,
                    "last_stored": self.last_stored
                },
                "settings": {
                    "similarity_threshold": self.similarity_threshold,
                    "update_threshold": self.update_threshold,
                    "milvus_host": self.milvus_config["host"],
                    "milvus_port": self.milvus_config["port"]
                },
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            raise

    async def clear(self):
        """Clear the vector cache and reset statistics"""
        try:
            if self.collection:
                # Delete all entities instead of dropping collection
                expr = "id >= 0"  # Match all entities
                self.collection.delete(expr)
                self.collection.flush()  # Ensure changes are persisted
                
                # Reset statistics
                self.total_hits = 0
                self.total_misses = 0
                self.last_hit = None
                self.last_miss = None
                self.last_stored = None
                
                logger.info("Cache entries and statistics cleared")
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
            raise

    async def _generate_embedding(self, query: str) -> list:
        """Generate embeddings optimized for HR domain"""
        try:
            # Preprocess query for HR context
            hr_query = f"job search: {query}"  # Add domain context
            embedding = self.embedding_model.encode(hr_query, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            raise
