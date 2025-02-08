from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    api_prefix: str = "/api"
    debug: bool = False
    
    cors_origins: List[str] = ["*"]
    
    # OpenAI settings
    model_name: str = "gpt-4o-mini"
    openai_api_key: str

    # Elasticsearch settings
    elasticsearch_host: str = "http://localhost:9200"
    elasticsearch_index: str = "hr_lens"

    milvus_host: str = Field(default="localhost")
    milvus_port: int = Field(default=19530)
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance with validation"""
    settings = Settings()
    return settings