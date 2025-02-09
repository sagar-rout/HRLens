from fastapi import FastAPI
from app.config import get_settings, Settings
from app.middleware import add_cors_middleware, add_error_handlers
from app.routes.base import add_routes


def create_app(settings: Settings | None = None) -> FastAPI:
    if settings is None:
        settings = get_settings()

    app = FastAPI(
        title="HR Lens - AI Agent",
        description="AI-powered HR search agent for natural language queries",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        debug=settings.debug,
    )

    add_cors_middleware(app)
    add_error_handlers(app)

    add_routes(app)

    return app
