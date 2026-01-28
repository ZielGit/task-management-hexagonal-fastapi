"""
API Middleware
Middleware personalizado para FastAPI
"""

from .error_handler import (
    domain_exception_handler,
    general_exception_handler,
    validation_exception_handler,
    http_exception_handler,
)
from .logging_middleware import (
    LoggingMiddleware,
    RequestContextMiddleware,
    get_request_id,
)

__all__ = [
    # Error handlers
    "domain_exception_handler",
    "general_exception_handler",
    "validation_exception_handler",
    "http_exception_handler",
    # Logging middleware
    "LoggingMiddleware",
    "RequestContextMiddleware",
    "get_request_id",
]
