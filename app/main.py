import uvicorn
from fastapi import FastAPI
from app.api.v1.search import router as search_router
from app.middleware.error_handlers import add_error_handlers
from app.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title="HRLens API",
        description="HR Analytics and Search API",
        version="1.0.0",
        debug=settings.debug
    )
    
    # Add routers
    app.include_router(search_router, prefix="/api/v1")
    
    # Add error handlers
    add_error_handlers(app)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=1,
        log_level="info"
    )
