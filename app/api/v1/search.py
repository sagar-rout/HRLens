from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from pydantic import BaseModel
from app.core.container import ServiceContainer
from app.config import Config
from app.utils.logger import logger
from app.core.cache_stats import CacheStats
import time

class SearchRequest(BaseModel):
    query: str

router = APIRouter()

@router.post("/search")
async def search(request: SearchRequest) -> Dict[str, Any]:
    """Execute a natural language search query"""
    try:
        container = ServiceContainer.get_instance()
        search_agent = container.get_search_agent()
        
        # Generate and execute search
        es_query, metrics = await search_agent.generate_es_query(request.query)
        results = container.get_es_client().search(body=es_query)
        
        return {
            "results": results,
            "metrics": {
                "cache_hit": metrics["cache_hit"],
                "search_time": time.time() - metrics.get("start_time", 0)
            }
        }
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.get("/cache/stats")
async def get_cache_stats() -> Dict[str, Any]:
    """Get detailed vector cache statistics"""
    try:
        container = ServiceContainer.get_instance()
        stats = container.get_cache_stats().get_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Failed to get cache stats: {str(e)}")
        return {
            "status": "error",
            "error": "Failed to retrieve cache statistics",
            "detail": str(e)
        }
