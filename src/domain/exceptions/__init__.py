"""
Domain Exceptions
Excepciones específicas del dominio de negocio
"""

from .base import DomainException
from .task_exceptions import (
    TaskException,
    TaskNotFoundException,
    InvalidTaskStateTransition,
    TaskAlreadyCompleted,
    TaskNotAssignable,
    TaskValidationError,
    TaskDeletionNotAllowed,
    UserNotFoundException,
    UnauthorizedOperationException,
)

__all__ = [
    "DomainException",
    "TaskException",
    "TaskNotFoundException",
    "InvalidTaskStateTransition",
    "TaskAlreadyCompleted",
    "TaskNotAssignable",
    "TaskValidationError",
    "TaskDeletionNotAllowed",
    "UserNotFoundException",
    "UnauthorizedOperationException",
]
