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
        self.distance_threshold = 0.2  # More restrictive threshold
        self.stats = CacheStats.get_instance(es_client)

        try:
            # Initialize Milvus connection
            connections.connect(
                alias="default", host=config["milvus_host"], port=config["milvus_port"]
            )
            self._init_collection()
            logger.info(f"Vector cache initialized: {self.collection_name}")
            self._initialized = True
        except Exception as e:
            logger.error(f"Cache initialization failed: {str(e)}")

    def _init_collection(self):
        """Initialize or create the cache collection"""
        try:
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                self.collection.load()
                logger.info(
                    f"Loaded existing cache with {self.collection.num_entities} entries"
                )
                return

            fields = [
                FieldSchema(
                    name="id", dtype=DataType.INT64, is_primary=True, auto_id=True
                ),
                FieldSchema(name="query_vector", dtype=DataType.FLOAT_VECTOR, dim=1536),
                FieldSchema(name="query_text", dtype=DataType.VARCHAR, max_length=500),
                FieldSchema(name="es_query", dtype=DataType.VARCHAR, max_length=4000),
                FieldSchema(name="created_at", dtype=DataType.INT64),
            ]

            schema = CollectionSchema(fields=fields, description="Semantic query cache")
            self.collection = Collection(name=self.collection_name, schema=schema)
            self.collection.create_index(
                field_name="query_vector",
                index_params={
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 128},
                },
            )
            self.collection.load()
            logger.info("Created new cache collection")

        except Exception as e:
            logger.error(f"Collection initialization failed: {str(e)}", exc_info=True)
            raise

    def _format_vector(self, embedding: list) -> list:
        """Format embedding for Milvus float vector"""
        try:
            embedding = np.array(embedding, dtype=np.float32).flatten()

            if embedding.shape[0] != 1536:
                raise ValueError(f"Expected 1536 dimensions, got {embedding.shape[0]}")

            return embedding.tolist()

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

            results = self.collection.search(
                data=[search_vector],
                anns_field="query_vector",
                param={"metric_type": "L2", "params": {"nprobe": 16}},
                limit=1,  # Only need the top result
                output_fields=["query_text", "es_query", "created_at"],
            )

            if not results or not results[0]:
                logger.debug("No results found in cache")
                self.stats.update(hit=False, query=query, is_store=False)
                return None

            hit = results[0][0]
            distance = hit.distance
            similarity = 1 - (distance / 2)  # L2 distance normalized

            if distance < self.distance_threshold:
                es_query = json.loads(hit.entity.get("es_query"))
                logger.info(
                    f"Cache hit: '{query}' matched '{hit.entity.get('query_text')}' "
                    f"(similarity: {similarity:.2%})"
                )
                self.stats.update(hit=True, query=query, is_store=False)
                return es_query

            logger.info(
                f"Cache miss - no matches above threshold ({self.distance_threshold})"
            )
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
            entity = {
                "query_vector": vector,
                "query_text": query,
                "es_query": json.dumps(es_query),
                "created_at": int(datetime.now().timestamp()),
            }

            self.collection.insert([entity])
            self.collection.flush()
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

    async def clear_cache(self):
        """Clear both vector cache and cache statistics."""
        try:
            # Release collection first
            if self.collection:
                self.collection.release()
                self.collection = None

            # Drop collection if exists
            if utility.has_collection(self.collection_name):
                utility.drop_collection(self.collection_name)
                logger.info(f"Cache collection '{self.collection_name}' dropped")

            # Wait for collection to be fully dropped
            while utility.has_collection(self.collection_name):
                await asyncio.sleep(0.5)

            # Reinitialize collection
            self._init_collection()
            
            # Verify collection is empty
            if self.collection.num_entities != 0:
                raise Exception("Cache collection not properly cleared")

            # Clear ES cache stats
            await self.stats.clear_stats()

            logger.info("Cache and statistics cleared successfully")
            return {"status": "success", "message": "Cache cleared successfully"}

        except Exception as e:
            error_msg = f"Failed to clear cache: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg)
