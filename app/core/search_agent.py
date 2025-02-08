from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from pydantic import SecretStr

from app.config import get_settings
from app.utils.logger import logger
from app.schema.templates.hr_system_template import HR_SYSTEM_TEMPLATE, documentation, es_mapping
import json

class SearchAgent:
    """Agent for converting natural language queries to Elasticsearch DSL"""
    
    def __init__(self):
        settings = get_settings()
        self.chat_model = ChatOpenAI(
            temperature=0,
            model=settings.model_name
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", HR_SYSTEM_TEMPLATE)
        ])
        
    async def generate_es_query(self, query: str) -> dict:
        """Generate Elasticsearch DSL query from natural language"""
        try:
            logger.info(f"Generating query for: {query}")
            
            chain = self.prompt | self.chat_model
            response = await chain.ainvoke({
                "documentation": documentation,
                "mapping": es_mapping,
                "query": query
            })
            
            generated_query = response.content
            logger.info(f"Raw LLM response:\n{generated_query}")
            return json.loads(generated_query)
            
        except Exception as e:
            logger.error(f"Failed to generate query: {str(e)}")
            raise 