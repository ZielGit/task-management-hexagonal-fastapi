from datetime import datetime
from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Query

from ....application.use_cases.create_task import CreateTaskUseCase
from ....application.use_cases.get_task import GetTaskUseCase
from ....application.use_cases.update_task import UpdateTaskUseCase
from ....application.use_cases.delete_task import DeleteTaskUseCase
from ....application.use_cases.list_tasks import ListTasksUseCase
from ....application.use_cases.assign_task import AssignTaskUseCase
from ....application.dtos.task_dto import (
    CreateTaskDTO,
    UpdateTaskDTO,
    AssignTaskDTO,
    TaskResponseDTO,
    TaskListResponseDTO,
    TaskDeletedResponseDTO,
    TaskFiltersDTO
)
from ....domain.value_objects.priority import Priority
from ....domain.value_objects.status import Status
from ....domain.exceptions.task_exceptions import (
    TaskNotFoundException,
    TaskValidationError,
    InvalidTaskStateTransition,
    TaskDeletionNotAllowed
)
from ..dependencies import (
    get_create_task_use_case,
    get_get_task_use_case,
    get_update_task_use_case,
    get_delete_task_use_case,
    get_list_tasks_use_case,
    get_assign_task_use_case,
    get_current_user_id
)


# Crear el router
router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["tasks"]
)


@router.post(
    "/",
    response_model=TaskResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    responses={
        201: {"description": "Task created successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Not authenticated"}
    }
)
async def create_task(
    dto: CreateTaskDTO,
    use_case: CreateTaskUseCase = Depends(get_create_task_use_case),
    current_user_id: UUID = Depends(get_current_user_id)
) -> TaskResponseDTO:
    """
    Crea una nueva tarea.
    
    - **title**: Título de la tarea (requerido, max 200 chars)
    - **description**: Descripción detallada (opcional, max 2000 chars)
    - **priority**: Prioridad (low, medium, high, urgent)
    - **auto_assign**: Auto-asignar al usuario actual
    """
    try:
        return await use_case.execute(dto, current_user_id)
    except TaskValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.get(
    "/{task_id}",
    response_model=TaskResponseDTO,
    summary="Get task by ID",
    responses={
        200: {"description": "Task found"},
        404: {"description": "Task not found"}
    }
)
async def get_task(
    task_id: UUID,
    use_case: GetTaskUseCase = Depends(get_get_task_use_case)
) -> TaskResponseDTO:
    """
    Obtiene una tarea por su ID.
    """
    try:
        return await use_case.execute(task_id)
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/",
    response_model=TaskListResponseDTO,
    summary="List tasks with filters",
    responses={
        200: {"description": "Tasks retrieved successfully"}
    }
)
async def list_tasks(
    status_filter: Status | None = Query(None, alias="status"),
    priority_filter: Priority | None = Query(None, alias="priority"),
    assigned_to: UUID | None = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    use_case: ListTasksUseCase = Depends(get_list_tasks_use_case)
) -> TaskListResponseDTO:
    """
    Lista tareas con filtros opcionales.
    
    - **status**: Filtrar por estado (todo, in_progress, done, cancelled)
    - **priority**: Filtrar por prioridad (low, medium, high, urgent)
    - **assigned_to**: Filtrar por usuario asignado (UUID)
    - **limit**: Número máximo de resultados (1-1000, default 100)
    - **offset**: Offset para paginación (default 0)
    """
    filters = TaskFiltersDTO(
        status=status_filter,
        priority=priority_filter,
        assigned_to=assigned_to,
        limit=limit,
        offset=offset
    )
    
    return await use_case.execute(filters)


@router.put(
    "/{task_id}",
    response_model=TaskResponseDTO,
    summary="Update task",
    responses={
        200: {"description": "Task updated successfully"},
        400: {"description": "Invalid state transition"},
        404: {"description": "Task not found"}
    }
)
async def update_task(
    task_id: UUID,
    dto: UpdateTaskDTO,
    use_case: UpdateTaskUseCase = Depends(get_update_task_use_case)
) -> TaskResponseDTO:
    """
    Actualiza una tarea existente.
    
    Permite actualizar: title, description, priority, status.
    Solo los campos proporcionados serán actualizados.
    """
    try:
        return await use_case.execute(task_id, dto)
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except (InvalidTaskStateTransition, TaskValidationError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{task_id}/assign",
    response_model=TaskResponseDTO,
    summary="Assign task to user",
    responses={
        200: {"description": "Task assigned successfully"},
        400: {"description": "Cannot assign task"},
        404: {"description": "Task not found"}
    }
)
async def assign_task(
    task_id: UUID,
    dto: AssignTaskDTO,
    use_case: AssignTaskUseCase = Depends(get_assign_task_use_case)
) -> TaskResponseDTO:
    """
    Asigna una tarea a un usuario específico.
    """
    try:
        return await use_case.execute(task_id, dto.user_id)
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/{task_id}",
    response_model=TaskDeletedResponseDTO,
    summary="Delete task",
    responses={
        200: {"description": "Task deleted successfully"},
        400: {"description": "Task cannot be deleted"},
        404: {"description": "Task not found"}
    }
)
async def delete_task(
    task_id: UUID,
    use_case: DeleteTaskUseCase = Depends(get_delete_task_use_case)
) -> TaskDeletedResponseDTO:
    """
    Elimina una tarea.
    
    Solo se pueden eliminar tareas canceladas o completadas hace más de 30 días.
    """
    try:
        await use_case.execute(task_id)
        return TaskDeletedResponseDTO(
            message="Task deleted successfully",
            task_id=task_id,
            deleted_at=datetime.utcnow()
        )
    except TaskNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except TaskDeletionNotAllowed as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
