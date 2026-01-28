from uuid import UUID
from ...domain.repositories.task_repository import TaskRepository
from ...domain.exceptions.task_exceptions import TaskNotFoundException
from ..dtos.task_dto import TaskResponseDTO


class GetTaskUseCase:
    """Caso de uso para obtener una tarea por ID"""
    
    def __init__(self, task_repository: TaskRepository):
        self._repository = task_repository
    
    async def execute(self, task_id: UUID) -> TaskResponseDTO:
        task = await self._repository.find_by_id(task_id)
        
        if task is None:
            raise TaskNotFoundException(str(task_id))
        
        return TaskResponseDTO(
            id=task.id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            status=task.status,
            assigned_to=task.assigned_to,
            created_at=task.created_at,
            updated_at=task.updated_at,
            completed_at=task.completed_at
        )
