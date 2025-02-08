from fastapi import FastAPI
from app.api.v1 import search
from app.api import health

def add_routes(app: FastAPI) -> None:
    app.include_router(health.router)
    
    app.include_router(
        search.router,
        prefix="/api"
    ) 