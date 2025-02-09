from elasticsearch import Elasticsearch
from typing import Dict, Any, Optional
from app.utils.logger import logger
import json


class ElasticsearchClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._client: Optional[Elasticsearch] = None

    @property
    def client(self) -> Elasticsearch:
        if self._client is None:
            self._client = self._create_client()
        return self._client

    def _create_client(self) -> Elasticsearch:
        try:
            client = Elasticsearch(
                hosts=self.config["hosts"],
                verify_certs=self.config.get("verify_certs", True),
            )
            if not client.ping():
                raise ConnectionError("Could not connect to Elasticsearch")
            return client
        except Exception as e:
            logger.error(f"Failed to create Elasticsearch client: {str(e)}")
            raise

    def search(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the provided search query"""
        try:
            logger.info(f"Executing search with query:\n{json.dumps(body, indent=2)}")
            response = self.client.search(
                index=self.config["elasticsearch_index"], body=body
            )
            logger.debug(f"Search response:\n{response}")
            return dict(response)
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise
