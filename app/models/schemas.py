from pydantic import BaseModel, Field
from typing import Any, Dict, List
from uuid import uuid4


class SearchRequest(BaseModel):
    query: str
    request_id: str = Field(default_factory=lambda: str(uuid4()))


class SearchResponse(BaseModel):
    query: Dict[str, Any]
    results: Dict[str, Any]
