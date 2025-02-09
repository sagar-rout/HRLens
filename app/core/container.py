from typing import Optional
from app.core.elasticsearch_client import ElasticsearchClient
from app.core.vector_cache import VectorCache
from app.core.cache_stats import CacheStats
from app.core.search_agent import SearchAgent
from app.core.services import (
    IElasticsearchClient,
    ICacheStats,
    IVectorCache,
    ISearchAgent,
)
from app.config import Config
from app.utils.logger import logger


class ServiceContainer:
    _instance = None
    _initialized = False

    # Service instances
    es_client: Optional[IElasticsearchClient] = None
    cache_stats: Optional[ICacheStats] = None
    vector_cache: Optional[IVectorCache] = None
    search_agent: Optional[ISearchAgent] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ServiceContainer, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialize_services()
        self._initialized = True

    def _initialize_services(self):
        """Initialize all service dependencies"""
        try:
            # Get config
            config = Config.get_config()

            # Initialize ES client first
            self.es_client = ElasticsearchClient(config["elasticsearch"])

            # Initialize cache stats
            self.cache_stats = CacheStats.get_instance(self.es_client)

            # Initialize vector cache
            self.vector_cache = VectorCache(config, self.es_client)

            # Initialize search agent
            self.search_agent = SearchAgent(self.es_client, self.vector_cache)

            logger.info("Service container initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize service container: {str(e)}")
            raise

    @classmethod
    def get_instance(cls) -> "ServiceContainer":
        """Get or create service container instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_es_client(self) -> IElasticsearchClient:
        return self.es_client

    def get_cache_stats(self) -> ICacheStats:
        return self.cache_stats

    def get_vector_cache(self) -> IVectorCache:
        return self.vector_cache

    def get_search_agent(self) -> ISearchAgent:
        return self.search_agent
