from uuid import UUID
from typing import Optional

from ...domain.entities.task import Task
from ...domain.repositories.task_repository import TaskRepository
from ...domain.value_objects.priority import Priority
from ...domain.value_objects.status import Status
from ...domain.exceptions.task_exceptions import TaskValidationError
from ..dtos.task_dto import CreateTaskDTO, TaskResponseDTO


class CreateTaskUseCase:
    """
    Caso de uso para crear una nueva tarea.
    Implementa la lógica de aplicación, no de dominio.
    """
    
    def __init__(self, task_repository: TaskRepository):
        """
        Inyección de dependencias del repositorio.
        
        Args:
            task_repository: Implementación del puerto TaskRepository
        """
        self._task_repository = task_repository
    
    async def execute(
        self,
        dto: CreateTaskDTO,
        created_by: UUID
    ) -> TaskResponseDTO:
        """
        Ejecuta el caso de uso de creación de tarea.
        
        Args:
            dto: DTO con los datos de entrada
            created_by: UUID del usuario que crea la tarea
            
        Returns:
            DTO con la tarea creada
            
        Raises:
            TaskValidationError: Si los datos no son válidos
        """
        # 1. Validar datos de entrada (aunque Pydantic ya valida mucho)
        await self._validate_input(dto)
        
        # 2. Crear la entidad de dominio
        task = self._create_task_entity(dto)
        
        # 3. Auto-asignar si se especificó
        if dto.auto_assign:
            task.assign_to(created_by)
        
        # 4. Persistir a través del repositorio
        saved_task = await self._task_repository.save(task)
        
        # 5. Retornar DTO de respuesta
        return self._to_response_dto(saved_task)
    
    async def _validate_input(self, dto: CreateTaskDTO) -> None:
        """
        Validaciones adicionales de negocio.
        
        Args:
            dto: DTO a validar
            
        Raises:
            TaskValidationError: Si hay errores de validación
        """
        # Ejemplo: validar que título no contenga palabras prohibidas
        forbidden_words = ["spam", "test123"]
        if any(word in dto.title.lower() for word in forbidden_words):
            raise TaskValidationError(
                f"Title contains forbidden words: {forbidden_words}"
            )
        
        # Ejemplo: validar que tareas URGENTES tengan descripción
        if dto.priority == Priority.URGENT and not dto.description.strip():
            raise TaskValidationError(
                "Urgent tasks must have a description"
            )
    
    def _create_task_entity(self, dto: CreateTaskDTO) -> Task:
        """
        Crea la entidad Task desde el DTO.
        
        Args:
            dto: DTO con los datos
            
        Returns:
            Nueva instancia de Task
        """
        return Task(
            title=dto.title,
            description=dto.description,
            priority=dto.priority,
            status=Status.TODO  # Siempre se crea en TODO
        )
    
    def _to_response_dto(self, task: Task) -> TaskResponseDTO:
        """
        Convierte la entidad Task a DTO de respuesta.
        
        Args:
            task: Entidad Task
            
        Returns:
            DTO de respuesta
        """
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
