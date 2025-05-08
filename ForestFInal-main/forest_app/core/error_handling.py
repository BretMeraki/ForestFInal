"""
Centralized error handling for Forest App.
Logs errors, provides user-friendly explanations, and actionable steps.
"""
import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)

# Map exception types to user-friendly explanations and steps
def get_error_explanation_and_steps(exc: Exception) -> dict:
    if isinstance(exc, RequestValidationError):
        return {
            "explanation": "The request data was invalid. This usually means a required field was missing or had the wrong type.",
            "steps": [
                "Check the API documentation for required fields and types.",
                "Ensure all required fields are included in your request.",
                "Correct any typos or formatting issues in your data."
            ]
        }
    # Add more mappings as needed
    return {
        "explanation": "An unexpected error occurred while processing your request.",
        "steps": [
            "Try your request again.",
            "If the problem persists, contact support and provide the error details.",
            "Check the server logs for more information."
        ]
    }

async def app_exception_handler(request: Request, exc: Exception):
    # Log with context
    logger.error(f"Unhandled exception at {request.url.path}: {exc}", exc_info=True)
    details = get_error_explanation_and_steps(exc)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": str(exc),
            "explanation": details["explanation"],
            "actionable_steps": details["steps"],
            "path": str(request.url.path)
        },
    )

# Optional: handler for validation errors
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error at {request.url.path}: {exc}", exc_info=True)
    details = get_error_explanation_and_steps(exc)
    return JSONResponse(
        status_code=422,
        content={
            "error": str(exc),
            "explanation": details["explanation"],
            "actionable_steps": details["steps"],
            "path": str(request.url.path)
        },
    )
