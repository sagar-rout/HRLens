from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import SearchRequest, SearchResponse
from app.core.search_agent import SearchAgent
from app.core.elasticsearch_client import ElasticsearchClient
from app.utils.logger import logger
from app.dependencies import get_search_agent, get_es_client

router = APIRouter(
    prefix="/v1/search",
    tags=["search"],
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal Server Error"},
        status.HTTP_400_BAD_REQUEST: {"description": "Bad Request"}
    }
)


@router.post(
    "/",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    description="Execute a natural language search query against the HR database"
)
async def search(
        request: SearchRequest,
        search_agent: SearchAgent = Depends(get_search_agent),
        es_client: ElasticsearchClient = Depends(get_es_client)
) -> SearchResponse:
    """
    Execute a natural language search query against the HR database.
    
    Args:
        request: Search request containing the natural language query
        search_agent: Injected search agent for query generation
        es_client: Injected Elasticsearch client
        
    Returns:
        SearchResponse containing the generated query and search results
    """
    try:
        logger.info(f"Processing search request: {request.query}")
        
        query = await search_agent.generate_es_query(request.query)
        results = await es_client.execute_query(query)
        
        logger.info("Search completed successfully")
        return SearchResponse(query=query, results=results)
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search request failed"
        )
