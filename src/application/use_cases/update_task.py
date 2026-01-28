from uuid import UUID
from typing import Optional
from ...domain.repositories.task_repository import TaskRepository
from ...domain.exceptions.task_exceptions import TaskNotFoundException
from ..dtos.task_dto import UpdateTaskDTO, TaskResponseDTO


class UpdateTaskUseCase:
    """Caso de uso para actualizar una tarea"""
    
    def __init__(self, task_repository: TaskRepository):
        self._repository = task_repository
    
    async def execute(
        self,
        task_id: UUID,
        dto: UpdateTaskDTO
    ) -> TaskResponseDTO:
        # Obtener tarea existente
        task = await self._repository.find_by_id(task_id)
        if task is None:
            raise TaskNotFoundException(str(task_id))
        
        # Aplicar actualizaciones
        if dto.title is not None:
            task.set_title(dto.title)
        
        if dto.description is not None:
            task.set_description(dto.description)
        
        if dto.priority is not None:
            task.change_priority(dto.priority)
        
        if dto.status is not None:
            self._update_status(task, dto.status)
        
        # Guardar cambios
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
    
    def _update_status(self, task, new_status):
        """Actualiza el estado según transiciones válidas"""
        from ...domain.value_objects.status import Status
        
        if new_status == Status.IN_PROGRESS:
            task.start()
        elif new_status == Status.DONE:
            task.complete()
        elif new_status == Status.CANCELLED:
            task.cancel()
        elif new_status == Status.TODO:
            task.reopen()
