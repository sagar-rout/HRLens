from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, Tuple
from app.config import get_settings
from app.utils.logger import logger
from app.schema.templates.hr_system_template import (
    HR_SYSTEM_TEMPLATE,
    documentation,
    es_mapping,
)
import json
import time
import numpy as np
from collections import OrderedDict


class SearchAgent:
    """Agent for converting natural language queries to Elasticsearch DSL"""

    def __init__(self, es_client, cache_stats, cache_size: int = 1000):
        settings = get_settings()
        self.chat_model = ChatOpenAI(temperature=0, model=settings.model_name)
        self.embeddings = OpenAIEmbeddings()
        self.prompt = ChatPromptTemplate.from_messages([("system", HR_SYSTEM_TEMPLATE)])
        self.es_client = es_client
        self.cache_stats = cache_stats

        # Simple LRU cache implementation
        self.cache_size = cache_size
        self.query_cache = OrderedDict()
        self.vector_cache = OrderedDict()

    async def generate_es_query(self, query: str) -> Tuple[Dict, Dict[str, Any]]:
        """Generate Elasticsearch query with caching"""
        metrics = {"cache_hit": False, "start_time": time.time()}

        try:
            query_vector = await self.embeddings.aembed_query(query)

            cached_result = await self._check_cache(query, query_vector)
            if cached_result:
                logger.debug(f"Cache hit: '{query}'")
                metrics["cache_hit"] = True
                self.cache_stats.update(hit=True, query=query)
                logger.debug(f"Cache result: {len(cached_result)}")
                return cached_result, metrics

            chain = self.prompt | self.chat_model
            response = await chain.ainvoke(
                {"documentation": documentation, "mapping": es_mapping, "query": query}
            )

            es_query = json.loads(response.content)
            logger.debug(f"Generated ES query: {json.dumps(es_query)}")

            # Store in cache
            self._store_in_cache(query, query_vector, es_query)
            self.cache_stats.update(hit=False, query=query, is_store=True)

            return es_query, metrics

        except Exception as e:
            logger.error(f"Query generation failed: {str(e)}")
            raise

    async def _check_cache(self, query: str, vector) -> Dict[str, Any]:
        """Check if query exists in cache"""
        # First check exact match
        if query in self.query_cache:
            self.query_cache.move_to_end(query)
            return self.query_cache[query]

        # Then check vector similarity
        if len(self.vector_cache) > 0:
            vector = np.array(vector)
            for cached_vector, cached_query in self.vector_cache.items():
                similarity = np.dot(vector, np.array(cached_vector)) / (
                    np.linalg.norm(vector) * np.linalg.norm(cached_vector)
                )
                if similarity > 0.95:  # High similarity threshold
                    self.vector_cache.move_to_end(cached_vector)
                    return self.query_cache[cached_query]
        return None

    def _store_in_cache(self, query: str, vector: list, es_query: Dict):
        """Store query in both caches"""
        # Maintain cache size limit
        if len(self.query_cache) >= self.cache_size:
            self.query_cache.popitem(last=False)
            self.vector_cache.popitem(last=False)

        # Store in both caches
        self.query_cache[query] = es_query
        vector_tuple = tuple(vector)  # Convert to hashable type
        self.vector_cache[vector_tuple] = query
