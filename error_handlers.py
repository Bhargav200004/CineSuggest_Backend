"""
Global error handlers for the Movie Recommendation API.
Ensures all errors are caught and returned with proper structure.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError, HTTPException
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from pydantic import ValidationError
import logging
from exceptions import MovieAPIException
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_error_response(
    status_code: int,
    message: str,
    error_type: str = "error",
    details: dict = None,
    path: str = None
) -> JSONResponse:
    """
    Create a standardized error response.
    """
    error_content = {
        "success": False,
        "error": {
            "type": error_type,
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    }
    
    if details:
        error_content["error"]["details"] = details
    
    if path:
        error_content["error"]["path"] = path
    
    return JSONResponse(
        status_code=status_code,
        content=error_content
    )


async def custom_exception_handler(request: Request, exc: MovieAPIException) -> JSONResponse:
    """
    Handler for custom MovieAPIException and its subclasses.
    """
    logger.error(
        f"Custom exception: {exc.message} | Path: {request.url.path} | "
        f"Status: {exc.status_code}"
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        error_type=exc.__class__.__name__,
        details=exc.details if exc.details else None,
        path=str(request.url.path)
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handler for FastAPI HTTPException.
    """
    logger.warning(
        f"HTTP exception: {exc.detail} | Path: {request.url.path} | "
        f"Status: {exc.status_code}"
    )
    
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        error_type="HTTPException",
        path=str(request.url.path)
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors (Pydantic).
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {len(errors)} validation errors | "
        f"Path: {request.url.path}"
    )
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Request validation failed",
        error_type="ValidationError",
        details={"validation_errors": errors},
        path=str(request.url.path)
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """
    Handler for SQLAlchemy database errors.
    """
    logger.error(
        f"Database error: {str(exc)} | Path: {request.url.path}",
        exc_info=True
    )
    
    # Handle specific database errors
    if isinstance(exc, IntegrityError):
        message = "Database integrity constraint violated"
        if "UNIQUE constraint failed" in str(exc):
            message = "Resource already exists"
        elif "FOREIGN KEY constraint failed" in str(exc):
            message = "Referenced resource does not exist"
    elif isinstance(exc, OperationalError):
        message = "Database connection error"
    else:
        message = "Database operation failed"
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message=message,
        error_type="DatabaseError",
        path=str(request.url.path)
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """
    Handler for Pydantic validation errors.
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Pydantic validation error: {len(errors)} errors | "
        f"Path: {request.url.path}"
    )
    
    return create_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Data validation failed",
        error_type="ValidationError",
        details={"validation_errors": errors},
        path=str(request.url.path)
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for any unhandled exceptions.
    This ensures no error crashes the application.
    """
    # Log the full traceback for debugging
    logger.error(
        f"Unhandled exception: {str(exc)} | Path: {request.url.path}",
        exc_info=True
    )
    
    # Log stack trace
    tb = traceback.format_exc()
    logger.error(f"Traceback:\n{tb}")
    
    return create_error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="An unexpected error occurred. Please try again later.",
        error_type="InternalServerError",
        details={"error_class": exc.__class__.__name__},
        path=str(request.url.path)
    )


def register_error_handlers(app):
    """
    Register all error handlers with the FastAPI application.
    """
    # Custom exceptions
    app.add_exception_handler(MovieAPIException, custom_exception_handler)
    
    # FastAPI exceptions
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # Database exceptions
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    
    # Pydantic validation
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    
    # Catch-all for any other exceptions
    app.add_exception_handler(Exception, generic_exception_handler)
    
    logger.info("All error handlers registered successfully")
