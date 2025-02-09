from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings


def add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to the application"""
    settings = get_settings()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
