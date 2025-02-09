from typing import Dict, Any
from datetime import datetime
from app.utils.logger import logger


class CacheStats:
    _instance = None
    _initialized = False

    @classmethod
    def get_instance(cls, es_client):
        if cls._instance is None:
            cls._instance = cls(es_client)
        return cls._instance

    def __init__(self, es_client):
        if self._initialized:
            return

        self.es_client = es_client
        self.stats_index = "cache_stats"
        self.logger = logger
        self._init_stats_index()
        self._initialized = True

    async def _init_stats_index(self):
        """Initialize Elasticsearch stats index"""
        try:
            exists = await self.es_client.indices.exists(index=self.stats_index)
            if not exists:
                mapping = {
                    "mappings": {
                        "properties": {
                            "total_hits": {"type": "long"},
                            "total_misses": {"type": "long"},
                            "queries_cached": {"type": "long"},
                            "last_hit": {
                                "properties": {
                                    "query": {"type": "text"},
                                    "time": {"type": "date"},
                                }
                            },
                            "last_miss": {
                                "properties": {
                                    "query": {"type": "text"},
                                    "time": {"type": "date"},
                                }
                            },
                        }
                    }
                }
                await self.es_client.indices.create(
                    index=self.stats_index, body=mapping
                )
                await self.es_client.index(
                    index=self.stats_index,
                    id="current",
                    body={"total_hits": 0, "total_misses": 0, "queries_cached": 0},
                )
        except Exception as e:
            self.logger.error(f"Failed to initialize stats index: {str(e)}")
            raise

    def update(self, hit: bool, query: str, is_store: bool = False):
        """Update cache statistics"""
        try:
            now = datetime.utcnow().isoformat()
            script = {
                "script": {
                    "source": """
                    ctx._source.total_hits += params.hit ? 1 : 0;
                    ctx._source.total_misses += params.hit ? 0 : 1;
                    ctx._source.queries_cached += params.is_store ? 1 : 0;
                    if (params.hit) {
                        ctx._source.last_hit = params.activity;
                    } else {
                        ctx._source.last_miss = params.activity;
                    }
                    """,
                    "lang": "painless",
                    "params": {
                        "hit": hit,
                        "is_store": is_store,
                        "activity": {"query": query, "time": now},
                    },
                }
            }
            self.es_client.client.update(
                index=self.stats_index, id="current", body=script
            )

        except Exception as e:
            logger.error(f"Failed to update stats: {str(e)}")

    def get_stats(self, total_entries: int = 0) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            stats = self.es_client.client.get(index=self.stats_index, id="current")[
                "_source"
            ]
            total_queries = stats.get("total_hits", 0) + stats.get("total_misses", 0)
            hit_rate = (
                (stats.get("total_hits", 0) / total_queries * 100)
                if total_queries > 0
                else 0
            )

            return {
                "performance": {
                    "total_queries": total_queries,
                    "hits": stats.get("total_hits", 0),
                    "misses": stats.get("total_misses", 0),
                    "hit_rate": f"{hit_rate:.1f}%",
                },
                "cache": {
                    "total_entries": total_entries,
                    "queries_cached": stats.get("queries_cached", 0),
                },
                "last_activity": {
                    "last_hit": stats.get("last_hit"),
                    "last_miss": stats.get("last_miss"),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get stats: {str(e)}")
            return {"error": f"Failed to retrieve statistics: {str(e)}"}

    async def clear_stats(self):
        """Clear all cache statistics from Elasticsearch"""
        try:
            await self.es_client.indices.delete(index=self.stats_index, ignore=[404])
            await self._init_stats_index()
            self.logger.info("Cache statistics cleared from Elasticsearch")
        except Exception as e:
            self.logger.error(f"Failed to clear cache statistics: {str(e)}")
            raise
