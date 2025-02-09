import os
from typing import Any, Dict
from app.core.vector_cache import VectorCache
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from elasticsearch import AsyncElasticsearch

router = APIRouter()


async def get_vector_cache() -> VectorCache:
    """Get or create VectorCache instance with proper configuration."""
    config: Dict[str, Any] = {
        "milvus_host": os.getenv("MILVUS_HOST", "localhost"),
        "milvus_port": os.getenv("MILVUS_PORT", "19530"),
    }

    # Initialize ES client with environment variables
    es_client = AsyncElasticsearch(os.getenv("ELASTICSEARCH_HOST"))

    # VectorCache is a singleton, so this will either create or return existing instance
    return VectorCache(config, es_client)


@router.post("/clear_cache")
async def clear_vector_cache(vector_cache: VectorCache = Depends(get_vector_cache)):
    """
    Endpoint to manually clear both vector cache and cache statistics (for development/testing).
    Clears:
    - Milvus vector cache collection
    - Elasticsearch cache statistics
    """
    try:
        await vector_cache.clear_cache()
        return JSONResponse(
            content={
                "message": "Cache cleared successfully",
                "details": "Both vector cache and statistics have been cleared",
            },
            status_code=200,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")
