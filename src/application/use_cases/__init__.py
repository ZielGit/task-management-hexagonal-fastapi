"""
Use Cases (Interactors)
Implementan la lógica de aplicación específica
"""
#Task Use Cases
from .create_task import CreateTaskUseCase
from .get_task import GetTaskUseCase
from .update_task import UpdateTaskUseCase
from .delete_task import DeleteTaskUseCase
from .list_tasks import ListTasksUseCase
from .assign_task import AssignTaskUseCase

#User Use Cases
from .register_user import RegisterUserUseCase
from .login_user import LoginUserUseCase
from .get_current_user import GetCurrentUserUseCase

__all__ = [
    #Task Use Cases
    "CreateTaskUseCase",
    "GetTaskUseCase",
    "UpdateTaskUseCase",
    "DeleteTaskUseCase",
    "ListTasksUseCase",
    "AssignTaskUseCase",
    #User Use Cases
    "RegisterUserUseCase",
    "LoginUserUseCase",
    "GetCurrentUserUseCase",
]
