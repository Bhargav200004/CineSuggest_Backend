"""
Custom exception classes for the Movie Recommendation API.
"""

class MovieAPIException(Exception):
    """Base exception for all Movie API custom exceptions."""
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(MovieAPIException):
    """Exception raised when a resource is not found."""
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message=message, status_code=404)


class UnauthorizedException(MovieAPIException):
    """Exception raised for authentication failures."""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(message=message, status_code=401)


class ForbiddenException(MovieAPIException):
    """Exception raised when access is forbidden."""
    def __init__(self, message: str = "Access forbidden"):
        super().__init__(message=message, status_code=403)


class BadRequestException(MovieAPIException):
    """Exception raised for invalid request data."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(message=message, status_code=400, details=details)


class ConflictException(MovieAPIException):
    """Exception raised for resource conflicts."""
    def __init__(self, resource: str, message: str = None):
        msg = message or f"{resource} already exists"
        super().__init__(message=msg, status_code=409)


class ValidationException(MovieAPIException):
    """Exception raised for validation errors."""
    def __init__(self, message: str, field: str = None):
        details = {"field": field} if field else {}
        super().__init__(message=message, status_code=422, details=details)


class DatabaseException(MovieAPIException):
    """Exception raised for database operation failures."""
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, status_code=500)


class RateLimitException(MovieAPIException):
    """Exception raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message=message, status_code=429)
