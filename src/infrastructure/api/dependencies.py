from typing import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from ...application.use_cases.create_task import CreateTaskUseCase
from ...application.use_cases.get_task import GetTaskUseCase
from ...application.use_cases.update_task import UpdateTaskUseCase
from ...application.use_cases.delete_task import DeleteTaskUseCase
from ...application.use_cases.list_tasks import ListTasksUseCase
from ...application.use_cases.assign_task import AssignTaskUseCase
from ..database.connection import get_db_session
from ..database.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from ..auth.jwt_service import JWTService


# Security scheme
security = HTTPBearer()


# ============= DATABASE DEPENDENCIES =============

async def get_task_repository(
    session: AsyncSession = Depends(get_db_session)
) -> SQLAlchemyTaskRepository:
    """
    Provee una instancia del repositorio de tareas.
    
    Args:
        session: Sesión de base de datos
        
    Returns:
        Repositorio de tareas
    """
    return SQLAlchemyTaskRepository(session)


# ============= USE CASE DEPENDENCIES =============

async def get_create_task_use_case(
    repository: SQLAlchemyTaskRepository = Depends(get_task_repository)
) -> CreateTaskUseCase:
    """Provee el caso de uso CreateTask"""
    return CreateTaskUseCase(repository)


async def get_get_task_use_case(
    repository: SQLAlchemyTaskRepository = Depends(get_task_repository)
) -> GetTaskUseCase:
    """Provee el caso de uso GetTask"""
    return GetTaskUseCase(repository)


async def get_update_task_use_case(
    repository: SQLAlchemyTaskRepository = Depends(get_task_repository)
) -> UpdateTaskUseCase:
    """Provee el caso de uso UpdateTask"""
    return UpdateTaskUseCase(repository)


async def get_delete_task_use_case(
    repository: SQLAlchemyTaskRepository = Depends(get_task_repository)
) -> DeleteTaskUseCase:
    """Provee el caso de uso DeleteTask"""
    return DeleteTaskUseCase(repository)


async def get_list_tasks_use_case(
    repository: SQLAlchemyTaskRepository = Depends(get_task_repository)
) -> ListTasksUseCase:
    """Provee el caso de uso ListTasks"""
    return ListTasksUseCase(repository)


async def get_assign_task_use_case(
    repository: SQLAlchemyTaskRepository = Depends(get_task_repository)
) -> AssignTaskUseCase:
    """Provee el caso de uso AssignTask"""
    return AssignTaskUseCase(repository)


# ============= AUTHENTICATION DEPENDENCIES =============

async def get_jwt_service() -> JWTService:
    """Provee el servicio JWT"""
    return JWTService()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(get_jwt_service)
) -> UUID:
    """
    Extrae y valida el usuario actual del token JWT.
    
    Args:
        credentials: Credenciales HTTP Bearer
        jwt_service: Servicio de JWT
        
    Returns:
        UUID del usuario autenticado
        
    Raises:
        HTTPException: Si el token es inválido o ha expirado
    """
    token = credentials.credentials
    
    try:
        payload = jwt_service.decode_token(token)
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return UUID(user_id)
    
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user_id(
    user_id: UUID = Depends(get_current_user_id)
) -> UUID:
    """
    Verifica que el usuario esté activo.
    
    En una implementación completa, aquí se verificaría
    contra la base de datos si el usuario está activo.
    
    Args:
        user_id: UUID del usuario
        
    Returns:
        UUID del usuario activo
    """
    # TODO: Verificar en BD que el usuario esté activo
    return user_id
