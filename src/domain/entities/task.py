from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from ..value_objects.priority import Priority
from ..value_objects.status import Status
from ..exceptions.task_exceptions import (
    InvalidTaskStateTransition,
    TaskAlreadyCompleted,
    TaskNotAssignable
)


class Task:
    """
    Entidad Task con encapsulación de lógica de negocio.
    No es una clase anémica - contiene comportamiento.
    """

    def __init__(
        self,
        title: str,
        description: str,
        priority: Priority,
        task_id: Optional[UUID] = None,
        status: Status = Status.TODO,
        assigned_to: Optional[UUID] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None
    ):
        self._id = task_id or uuid4()
        self._title = ""
        self._description = ""
        self._priority = priority
        self._status = status
        self._assigned_to = assigned_to
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._completed_at = completed_at
        
        # Validaciones en construcción
        self.set_title(title)
        self.set_description(description)
    
    # ============= GETTERS =============
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def title(self) -> str:
        return self._title
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def priority(self) -> Priority:
        return self._priority
    
    @property
    def status(self) -> Status:
        return self._status
    
    @property
    def assigned_to(self) -> Optional[UUID]:
        return self._assigned_to
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        return self._completed_at
    
    # ============= COMPORTAMIENTO (Lógica de Negocio) =============
    
    def set_title(self, title: str) -> None:
        """Valida y establece el título"""
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title cannot be empty")
        
        if len(title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        
        self._title = title.strip()
        self._mark_as_updated()
    
    def set_description(self, description: str) -> None:
        """Valida y establece la descripción"""
        if len(description) > 2000:
            raise ValueError("Task description cannot exceed 2000 characters")
        
        self._description = description.strip()
        self._mark_as_updated()
    
    def change_priority(self, new_priority: Priority) -> None:
        """Cambia la prioridad de la tarea"""
        if self.is_completed():
            raise TaskAlreadyCompleted("Cannot change priority of completed task")
        
        self._priority = new_priority
        self._mark_as_updated()
    
    def assign_to(self, user_id: UUID) -> None:
        """Asigna la tarea a un usuario"""
        if self.is_completed():
            raise TaskNotAssignable("Cannot assign completed task")
        
        if self.is_cancelled():
            raise TaskNotAssignable("Cannot assign cancelled task")
        
        self._assigned_to = user_id
        self._mark_as_updated()
    
    def unassign(self) -> None:
        """Desasigna la tarea"""
        self._assigned_to = None
        self._mark_as_updated()
    
    def start(self) -> None:
        """Inicia el trabajo en la tarea"""
        if self._status != Status.TODO:
            raise InvalidTaskStateTransition(
                f"Cannot start task from status {self._status.value}"
            )
        
        self._status = Status.IN_PROGRESS
        self._mark_as_updated()
    
    def complete(self) -> None:
        """Marca la tarea como completada"""
        if self._status == Status.CANCELLED:
            raise InvalidTaskStateTransition("Cannot complete a cancelled task")
        
        if self._status == Status.DONE:
            raise TaskAlreadyCompleted("Task is already completed")
        
        self._status = Status.DONE
        self._completed_at = datetime.utcnow()
        self._mark_as_updated()
    
    def cancel(self) -> None:
        """Cancela la tarea"""
        if self._status == Status.DONE:
            raise InvalidTaskStateTransition("Cannot cancel a completed task")
        
        if self._status == Status.CANCELLED:
            return  # Idempotente
        
        self._status = Status.CANCELLED
        self._mark_as_updated()
    
    def reopen(self) -> None:
        """Reabre una tarea cancelada o completada"""
        if self._status not in [Status.DONE, Status.CANCELLED]:
            raise InvalidTaskStateTransition(
                f"Cannot reopen task with status {self._status.value}"
            )
        
        self._status = Status.TODO
        self._completed_at = None
        self._mark_as_updated()
    
    # ============= CONSULTAS (Query Methods) =============
    
    def is_completed(self) -> bool:
        """Verifica si la tarea está completada"""
        return self._status == Status.DONE
    
    def is_cancelled(self) -> bool:
        """Verifica si la tarea está cancelada"""
        return self._status == Status.CANCELLED
    
    def is_assigned(self) -> bool:
        """Verifica si la tarea está asignada"""
        return self._assigned_to is not None
    
    def is_high_priority(self) -> bool:
        """Verifica si la tarea es de alta prioridad"""
        return self._priority in [Priority.HIGH, Priority.URGENT]
    
    def can_be_deleted(self) -> bool:
        """Verifica si la tarea puede ser eliminada"""
        # Regla de negocio: solo tareas canceladas o completadas hace más de 30 días
        if self._status == Status.CANCELLED:
            return True
        
        if self._status == Status.DONE and self._completed_at:
            days_since_completion = (datetime.utcnow() - self._completed_at).days
            return days_since_completion > 30
        
        return False
    
    # ============= MÉTODOS PRIVADOS =============
    
    def _mark_as_updated(self) -> None:
        """Actualiza el timestamp de modificación"""
        self._updated_at = datetime.utcnow()
    
    # ============= MÉTODOS MÁGICOS =============
    
    def __eq__(self, other: object) -> bool:
        """Dos tareas son iguales si tienen el mismo ID"""
        if not isinstance(other, Task):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash basado en el ID"""
        return hash(self._id)
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self._id}, title='{self._title}', "
            f"status={self._status.value}, priority={self._priority.value})"
        )
