"""FastAPI exception handlers for Forest application."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from forest_app.core.exceptions import (
    StateLoadError,
    StateSaveError,
    ProcessingError,
    WitheringError
)

async def state_load_error_handler(request: Request, exc: StateLoadError) -> JSONResponse:
    """Handle state loading errors with 503 Service Unavailable."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "State Load Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

async def state_save_error_handler(request: Request, exc: StateSaveError) -> JSONResponse:
    """Handle state saving errors with 503 Service Unavailable."""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "State Save Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

async def processing_error_handler(request: Request, exc: ProcessingError) -> JSONResponse:
    """Handle processing errors with 500 Internal Server Error."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Processing Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

async def withering_error_handler(request: Request, exc: WitheringError) -> JSONResponse:
    """Handle withering calculation errors with 500 Internal Server Error."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Withering Error",
            "detail": str(exc),
            "path": request.url.path
        }
    )

def register_exception_handlers(app):
    """Register all custom exception handlers with the FastAPI app."""
    app.add_exception_handler(StateLoadError, state_load_error_handler)
    app.add_exception_handler(StateSaveError, state_save_error_handler)
    app.add_exception_handler(ProcessingError, processing_error_handler)
    app.add_exception_handler(WitheringError, withering_error_handler) 