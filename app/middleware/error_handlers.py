from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils.logger import logger


def add_error_handlers(app: FastAPI) -> None:
    """Add global error handlers to the application"""

    @app.exception_handler(Exception)
    async def global_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=500, content={"detail": "Internal server error"}
        )
