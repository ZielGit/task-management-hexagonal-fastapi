from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from ..entities.task import Task
from ..value_objects.priority import Priority
from ..value_objects.status import Status


class TaskRepository(ABC):
    """
    Interface del repositorio de Task (Puerto).
    La capa de dominio define QUÉ necesita, no CÓMO se implementa.
    """
    
    @abstractmethod
    async def save(self, task: Task) -> Task:
        """
        Persiste una nueva tarea o actualiza una existente.
        
        Args:
            task: Entidad Task a persistir
            
        Returns:
            La tarea persistida
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, task_id: UUID) -> Optional[Task]:
        """
        Busca una tarea por su ID.
        
        Args:
            task_id: UUID de la tarea
            
        Returns:
            La tarea si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def find_all(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        assigned_to: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Task]:
        """
        Lista tareas con filtros opcionales.
        
        Args:
            status: Filtrar por estado
            priority: Filtrar por prioridad
            assigned_to: Filtrar por usuario asignado
            limit: Número máximo de resultados
            offset: Offset para paginación
            
        Returns:
            Lista de tareas que cumplen los criterios
        """
        pass
    
    @abstractmethod
    async def delete(self, task_id: UUID) -> bool:
        """
        Elimina una tarea por su ID.
        
        Args:
            task_id: UUID de la tarea a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        pass
    
    @abstractmethod
    async def exists(self, task_id: UUID) -> bool:
        """
        Verifica si existe una tarea con el ID dado.
        
        Args:
            task_id: UUID de la tarea
            
        Returns:
            True si existe, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def count(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        assigned_to: Optional[UUID] = None
    ) -> int:
        """
        Cuenta el número de tareas que cumplen los criterios.
        
        Args:
            status: Filtrar por estado
            priority: Filtrar por prioridad
            assigned_to: Filtrar por usuario asignado
            
        Returns:
            Número de tareas
        """
        pass
    
    @abstractmethod
    async def find_by_assigned_user(
        self,
        user_id: UUID,
        status: Optional[Status] = None
    ) -> List[Task]:
        """
        Busca todas las tareas asignadas a un usuario.
        
        Args:
            user_id: UUID del usuario
            status: Filtrar adicionalmente por estado
            
        Returns:
            Lista de tareas asignadas al usuario
        """
        pass
