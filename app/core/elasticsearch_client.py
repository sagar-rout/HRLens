from elasticsearch import AsyncElasticsearch
from app.config import get_settings
from app.utils.logger import logger
import json

class ElasticsearchClient:
    def __init__(self):
        self.settings = get_settings()
        self.client = AsyncElasticsearch(self.settings.elasticsearch_host)
        self.index = self.settings.elasticsearch_index

    async def execute_query(self, query: dict) -> dict:
        """Execute Elasticsearch query and return appropriate response"""
        try:
            logger.info(f"Executing Elasticsearch query:\n{json.dumps(query, indent=2)}")
            
            response = await self.client.search(
                index=self.index,
                body=query
            )
            
            response_dict = dict(response)
            logger.info(f"Elasticsearch response:{response_dict}")
            return response_dict
            
        except Exception as e:
            logger.error(f"Error executing Elasticsearch query: {str(e)}\nQuery body:\n{json.dumps(query, indent=2)}")
            raise

    async def close(self):
        await self.client.close() 