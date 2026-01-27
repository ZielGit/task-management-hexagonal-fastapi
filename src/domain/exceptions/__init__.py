"""
Domain Exceptions
Excepciones específicas del dominio de negocio
"""

from .task_exceptions import (
    DomainException,
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
