from functools import lru_cache
from typing import List, Dict, Any
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

class Config:
    @staticmethod
    def get_config() -> Dict[str, Any]:
        return {
            "elasticsearch": {
                "hosts": os.getenv("ES_HOSTS", "http://localhost:9200").split(","),
                "verify_certs": os.getenv("ES_VERIFY_CERTS", "true").lower() == "true",
                "elasticsearch_index": os.getenv("ELASTICSEARCH_INDEX", "hr_lens")
            },
            "logging": {
                "level": os.getenv("LOG_LEVEL", "INFO"),
                "file_path": os.getenv("LOG_FILE", "logs/app.log")
            },
            "api": {
                "version": "v1",
                "prefix": "/api/v1"
            }
        }