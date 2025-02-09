import uvicorn
from app.core.factory import create_app
from fastapi import FastAPI, Depends
from app.core.vector_cache import VectorCache
from typing import Any, Dict

app = create_app()


def main() -> None:
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload
        workers=1,  # Use single worker for development
        log_level="debug",
        reload_dirs=["app"],  # Only watch the app directory for changes
        reload_excludes=["*.pyc", "*.pyo", "*.pyd", "__pycache__"],
    )


if __name__ == "__main__":
    main()
