from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from typing import Dict, Any, Tuple
from app.config import get_settings
from app.utils.logger import logger
from app.schema.templates.hr_system_template import HR_SYSTEM_TEMPLATE, documentation, es_mapping
from app.core.services import IVectorCache
import json
import time

class SearchAgent:
    """Agent for converting natural language queries to Elasticsearch DSL"""
    
    def __init__(self, es_client, vector_cache: IVectorCache):
        settings = get_settings()
        self.chat_model = ChatOpenAI(
            temperature=0,
            model=settings.model_name
        )
        self.embeddings = OpenAIEmbeddings()
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", HR_SYSTEM_TEMPLATE)
        ])
        self.es_client = es_client
        self.cache = vector_cache

    async def generate_es_query(self, query: str) -> Tuple[Dict, Dict[str, Any]]:
        """Generate Elasticsearch query with caching"""
        metrics = {
            "cache_hit": False,
            "start_time": time.time()
        }
        
        try:
            # Generate embeddings for the query
            query_vector = await self.embeddings.aembed_query(query)
            
            # Check cache first
            cached_query = await self.cache.find_query(query, query_vector)
            if cached_query:
                metrics["cache_hit"] = True
                return cached_query, metrics
            
            # Generate new query using LLM
            chain = self.prompt | self.chat_model
            response = await chain.ainvoke({
                "documentation": documentation,
                "mapping": es_mapping,
                "query": query
            })
            
            es_query = json.loads(response.content)
            
            # Cache the new query
            await self.cache.store_query(query, query_vector, es_query)
            
            return es_query, metrics
            
        except Exception as e:
            logger.error(f"Query generation failed: {str(e)}")
            raise 