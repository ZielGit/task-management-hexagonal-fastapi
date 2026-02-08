"""
Repository Ports (Interfaces)
Define contratos que debe implementar la infraestructura
"""

from .task_repository import TaskRepository
from .user_repository import UserRepository

__all__ = ["TaskRepository", "UserRepository"]
