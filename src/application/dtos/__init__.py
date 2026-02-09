"""
Data Transfer Objects
Objetos para transferir datos entre capas
"""

# Task DTOs
from .task_dto import (
    CreateTaskDTO,
    UpdateTaskDTO,
    AssignTaskDTO,
    TaskFiltersDTO,
    TaskResponseDTO,
    TaskListResponseDTO,
    TaskDeletedResponseDTO,
)

# User DTOs
from .user_dto import (
    RegisterUserDTO,
    LoginUserDTO,
    UserResponseDTO,
    TokenResponseDTO,
)

__all__ = [
    # Task DTOs
    "CreateTaskDTO",
    "UpdateTaskDTO",
    "AssignTaskDTO",
    "TaskFiltersDTO",
    "TaskResponseDTO",
    "TaskListResponseDTO",
    "TaskDeletedResponseDTO",
    # User DTOs
    "RegisterUserDTO",
    "LoginUserDTO",
    "UserResponseDTO",
    "TokenResponseDTO",
]
