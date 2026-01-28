"""
API Routes
Endpoints HTTP de la aplicación
"""

from . import tasks, auth, health

# Exportar los routers para facilitar el registro en main.py
task_router = tasks.router
auth_router = auth.router
health_router = health.router

__all__ = [
    # Módulos completos
    "tasks",
    "auth",
    "health",
    # Routers individuales
    "task_router",
    "auth_router",
    "health_router",
]
