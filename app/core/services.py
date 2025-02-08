from typing import Protocol, Dict, Any, Optional
from datetime import datetime

class IElasticsearchClient(Protocol):
    def search(self, body: Dict[str, Any]) -> Dict[str, Any]:
        ...

class ICacheStats(Protocol):
    def update(self, hit: bool, query: str, is_store: bool = False) -> None:
        ...
    def get_stats(self, total_entries: int = 0) -> Dict[str, Any]:
        ...

class IVectorCache(Protocol):
    async def find_query(self, query: str, embedding: list) -> Optional[Dict]:
        ...
    async def store_query(self, query: str, embedding: list, es_query: Dict) -> None:
        ...
    def get_stats(self) -> Dict[str, Any]:
        ...

class ISearchAgent(Protocol):
    async def generate_es_query(self, query: str) -> tuple[Dict, Dict[str, Any]]:
        ... 