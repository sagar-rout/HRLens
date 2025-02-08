from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.core.search_agent import SearchAgent
from app.core.elasticsearch_client import ElasticsearchClient
from app.config import Config
from app.utils.logger import logger

class SearchRequest(BaseModel):
    query: str

router = APIRouter()

@router.post("/search")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """
    Execute a natural language search query against the configured Elasticsearch index
    """
    try:
        config = Config.get_config()
        es_client = ElasticsearchClient(config["elasticsearch"])
        search_agent = SearchAgent(es_client)
        
        es_query = await search_agent.generate_es_query(request.query)
        
        results = es_client.search(body=es_query)
        return results
    except Exception as e:
        logger.error(f"Search endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
