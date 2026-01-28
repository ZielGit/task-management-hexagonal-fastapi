from uuid import UUID
from ...domain.repositories.task_repository import TaskRepository
from ...domain.exceptions.task_exceptions import TaskNotFoundException
from ..dtos.task_dto import TaskResponseDTO


class AssignTaskUseCase:
    """Caso de uso para asignar una tarea a un usuario"""
    
    def __init__(self, task_repository: TaskRepository):
        self._repository = task_repository
    
    async def execute(self, task_id: UUID, user_id: UUID) -> TaskResponseDTO:
        # Obtener tarea
        task = await self._repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(str(task_id))
        
        # Asignar (validación dentro de la entidad)
        task.assign_to(user_id)
        
        # Guardar
        updated_task = await self._repository.save(task)
        
        return TaskResponseDTO(
            id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            priority=updated_task.priority,
            status=updated_task.status,
            assigned_to=updated_task.assigned_to,
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at,
            completed_at=updated_task.completed_at
        )
