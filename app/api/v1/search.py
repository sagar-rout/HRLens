from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, AsyncGenerator
from pydantic import BaseModel
from app.core.search_agent import SearchAgent
from app.core.elasticsearch_client import ElasticsearchClient
from app.core.cache_stats import CacheStats
from app.config import Config
from app.utils.logger import logger
import time
from app.core.vector_cache import VectorCache


class SearchRequest(BaseModel):
    query: str


router = APIRouter()

async def get_services() -> AsyncGenerator[tuple, None]:
    """Initialize services with proper configuration"""
    config = Config.get_config()
    
    # Initialize services
    es_client = ElasticsearchClient(config["elasticsearch"])
    
    # Get or create VectorCache singleton
    vector_cache = VectorCache({
        "host": config["milvus"]["host"],
        "port": config["milvus"]["port"]
    })
    
    # Initialize only if not already initialized
    if not VectorCache._initialized:
        await vector_cache.initialize()
    
    search_agent = SearchAgent(es_client, vector_cache)
    
    try:
        yield es_client, vector_cache, search_agent
    finally:
        await es_client.close()

@router.post("/search")
async def search(
    request: SearchRequest,
    services: tuple = Depends(get_services)
) -> Dict[str, Any]:
    """Execute a natural language search query"""
    es_client, vector_cache, search_agent = services
    
    try:
        es_query, metrics = await search_agent.generate_es_query(request.query)
        results = await es_client.search(body=es_query)
        
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
async def get_cache_stats(
    services: tuple = Depends(get_services)
) -> Dict[str, Any]:
    """Get detailed vector cache statistics"""
    try:
        _, vector_cache, _ = services
        stats = await vector_cache.get_stats()
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

@router.post("/cache/clear")
async def clear_cache(
    services: tuple = Depends(get_services)
) -> Dict[str, Any]:
    """Clear cache and statistics"""
    try:
        _, vector_cache, _ = services
        
        # Clear Milvus vector cache
        await vector_cache.clear()
        
        return {
            "status": "success",
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {str(e)}")
        return {
            "status": "error",
            "error": "Failed to clear cache",
            "detail": str(e)
        }
