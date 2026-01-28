from ...domain.repositories.task_repository import TaskRepository
from ..dtos.task_dto import TaskFiltersDTO, TaskListResponseDTO, TaskResponseDTO


class ListTasksUseCase:
    """Caso de uso para listar tareas con filtros"""
    
    def __init__(self, task_repository: TaskRepository):
        self._repository = task_repository
    
    async def execute(self, filters: TaskFiltersDTO) -> TaskListResponseDTO:
        # Obtener tareas con filtros
        tasks = await self._repository.find_all(
            status=filters.status,
            priority=filters.priority,
            assigned_to=filters.assigned_to,
            limit=filters.limit,
            offset=filters.offset
        )
        
        # Obtener total para paginación
        total = await self._repository.count(
            status=filters.status,
            priority=filters.priority,
            assigned_to=filters.assigned_to
        )
        
        # Convertir a DTOs
        task_dtos = [
            TaskResponseDTO(
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
            for task in tasks
        ]
        
        return TaskListResponseDTO(
            tasks=task_dtos,
            total=total,
            limit=filters.limit,
            offset=filters.offset
        )
