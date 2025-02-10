from elasticsearch import AsyncElasticsearch
from typing import Dict, Any, Optional
from app.utils.logger import logger
import json
from contextlib import asynccontextmanager


class ElasticsearchClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._client: Optional[AsyncElasticsearch] = None

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()

    @property
    def client(self) -> AsyncElasticsearch:
        if self._client is None:
            self._client = self._create_client()
        return self._client

    @property
    def indices(self):
        """Expose the indices API of the native client"""
        return self.client.indices

    def _create_client(self) -> AsyncElasticsearch:
        try:
            return AsyncElasticsearch(
                hosts=self.config["hosts"],
                verify_certs=self.config.get("verify_certs", True),
            )
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch client: {str(e)}")
            raise

    async def search(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the provided search query"""
        try:
            logger.info(f"Executing search with query:\n{json.dumps(body, indent=2)}")
            response = await self.client.search(
                index=self.config["elasticsearch_index"], 
                body=body
            )
            return dict(response)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    async def close(self):
        """Close the client connection"""
        if self._client:
            await self._client.close()
            self._client = None

# Add dependency function for ElasticsearchClient
def get_es_client() -> ElasticsearchClient:
    config = {
        "hosts": ["http://localhost:9200"],
        "elasticsearch_index": "your_index_name",  # update as needed
        "verify_certs": True,
    }
    return ElasticsearchClient(config)
