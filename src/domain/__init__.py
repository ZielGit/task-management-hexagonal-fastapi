"""
Domain Layer - Núcleo del negocio
Contiene entidades, value objects, repositorios (puertos) y excepciones
"""

# Exportar para facilitar imports
from .entities.task import Task
from .value_objects.priority import Priority
from .value_objects.status import Status
from .repositories.task_repository import TaskRepository

__all__ = [
    "Task",
    "Priority",
    "Status",
    "TaskRepository",
]
