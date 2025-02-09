from app.core.search_agent import SearchAgent
from app.core.elasticsearch_client import ElasticsearchClient


async def get_search_agent() -> SearchAgent:
    """
    Dependency provider for SearchAgent instance.
    """
    return SearchAgent()


async def get_es_client():
    """
    Dependency provider for ElasticsearchClient instance.
    """
    client = ElasticsearchClient()
    try:
        yield client
    finally:
        await client.close()
