from uuid import UUID
from ...domain.repositories.task_repository import TaskRepository
from ...domain.exceptions.task_exceptions import (
    TaskNotFoundException,
    TaskDeletionNotAllowed
)


class DeleteTaskUseCase:
    """Caso de uso para eliminar una tarea"""
    
    def __init__(self, task_repository: TaskRepository):
        self._repository = task_repository
    
    async def execute(self, task_id: UUID) -> None:
        # Obtener tarea
        task = await self._repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(str(task_id))
        
        # Verificar si puede ser eliminada
        if not task.can_be_deleted():
            raise TaskDeletionNotAllowed(
                str(task_id),
                f"Task with status '{task.status.value}' cannot be deleted"
            )
        
        # Eliminar
        await self._repository.delete(task_id)
