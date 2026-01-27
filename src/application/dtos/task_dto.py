from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from ...domain.value_objects.priority import Priority
from ...domain.value_objects.status import Status


# ============= INPUT DTOs =============

class CreateTaskDTO(BaseModel):
    """DTO para crear una nueva tarea"""
    
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title"
    )
    description: str = Field(
        default="",
        max_length=2000,
        description="Task description"
    )
    priority: Priority = Field(
        default=Priority.MEDIUM,
        description="Task priority level"
    )
    auto_assign: bool = Field(
        default=False,
        description="Auto-assign to creator"
    )
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        """Valida que el título no esté vacío después de strip"""
        if not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Normaliza la descripción"""
        return v.strip()
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Implement user authentication",
                    "description": "Add JWT authentication to the API",
                    "priority": "high",
                    "auto_assign": True
                }
            ]
        }
    }


class UpdateTaskDTO(BaseModel):
    """DTO para actualizar una tarea existente"""
    
    title: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=200
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000
    )
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty or whitespace")
        return v.strip() if v else None
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated title",
                    "priority": "urgent",
                    "status": "in_progress"
                }
            ]
        }
    }


class AssignTaskDTO(BaseModel):
    """DTO para asignar una tarea a un usuario"""
    
    user_id: UUID = Field(
        ...,
        description="ID of the user to assign the task to"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "123e4567-e89b-12d3-a456-426614174000"
                }
            ]
        }
    }


class TaskFiltersDTO(BaseModel):
    """DTO para filtrar tareas"""
    
    status: Optional[Status] = Field(
        default=None,
        description="Filter by status"
    )
    priority: Optional[Priority] = Field(
        default=None,
        description="Filter by priority"
    )
    assigned_to: Optional[UUID] = Field(
        default=None,
        description="Filter by assigned user"
    )
    limit: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of results"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Offset for pagination"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "todo",
                    "priority": "high",
                    "limit": 50,
                    "offset": 0
                }
            ]
        }
    }


# ============= OUTPUT DTOs =============

class TaskResponseDTO(BaseModel):
    """DTO de respuesta con datos de una tarea"""
    
    id: UUID
    title: str
    description: str
    priority: Priority
    status: Status
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "title": "Implement authentication",
                    "description": "Add JWT auth to API",
                    "priority": "high",
                    "status": "in_progress",
                    "assigned_to": "987fcdeb-51a2-43f1-b456-426614174999",
                    "created_at": "2024-01-15T10:30:00Z",
                    "updated_at": "2024-01-15T14:20:00Z",
                    "completed_at": None
                }
            ]
        }
    }


class TaskListResponseDTO(BaseModel):
    """DTO de respuesta para lista de tareas con paginación"""
    
    tasks: list[TaskResponseDTO]
    total: int
    limit: int
    offset: int
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "tasks": [],
                    "total": 150,
                    "limit": 100,
                    "offset": 0
                }
            ]
        }
    }


class TaskDeletedResponseDTO(BaseModel):
    """DTO de respuesta para eliminación de tarea"""
    
    message: str
    task_id: UUID
    deleted_at: datetime
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "Task deleted successfully",
                    "task_id": "123e4567-e89b-12d3-a456-426614174000",
                    "deleted_at": "2024-01-15T16:45:00Z"
                }
            ]
        }
    }
