"""
Repository Ports (Interfaces)
Define contratos que debe implementar la infraestructura
"""

from .task_repository import TaskRepository

__all__ = ["TaskRepository"]