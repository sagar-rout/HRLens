from fastapi import FastAPI
from app.api.maintenance import cache
from app.api.v1 import search
from app.api import health


def add_routes(app: FastAPI) -> None:
    app.include_router(health.router)

    app.include_router(search.router, prefix="/api")
    app.include_router(cache.router, prefix="/api")
