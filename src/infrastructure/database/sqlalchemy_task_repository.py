from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.task import Task
from ...domain.repositories.task_repository import TaskRepository
from ...domain.value_objects.priority import Priority
from ...domain.value_objects.status import Status
from .models import TaskModel


class SQLAlchemyTaskRepository(TaskRepository):
    """
    Implementación del repositorio usando SQLAlchemy.
    Traduce entre entidades de dominio y modelos de BD.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Args:
            session: Sesión de SQLAlchemy para operaciones de BD
        """
        self._session = session
    
    async def save(self, task: Task) -> Task:
        """
        Persiste una tarea (insert o update).
        
        Args:
            task: Entidad Task del dominio
            
        Returns:
            La tarea persistida
        """
        # Buscar si ya existe
        stmt = select(TaskModel).where(TaskModel.id == task.id)
        result = await self._session.execute(stmt)
        db_task = result.scalar_one_or_none()
        
        if db_task:
            # UPDATE: actualizar modelo existente
            self._update_model_from_entity(db_task, task)
        else:
            # INSERT: crear nuevo modelo
            db_task = self._to_model(task)
            self._session.add(db_task)
        
        await self._session.flush()
        await self._session.refresh(db_task)
        
        return self._to_entity(db_task)
    
    async def find_by_id(self, task_id: UUID) -> Optional[Task]:
        """
        Busca una tarea por ID.
        
        Args:
            task_id: UUID de la tarea
            
        Returns:
            Entidad Task si existe, None en caso contrario
        """
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        db_task = result.scalar_one_or_none()
        
        if db_task is None:
            return None
        
        return self._to_entity(db_task)
    
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
        
        Returns:
            Lista de entidades Task
        """
        stmt = select(TaskModel)
        
        # Aplicar filtros
        if status is not None:
            stmt = stmt.where(TaskModel.status == status.value)
        
        if priority is not None:
            stmt = stmt.where(TaskModel.priority == priority.value)
        
        if assigned_to is not None:
            stmt = stmt.where(TaskModel.assigned_to == assigned_to)
        
        # Ordenar por fecha de creación (más recientes primero)
        stmt = stmt.order_by(TaskModel.created_at.desc())
        
        # Paginación
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self._session.execute(stmt)
        db_tasks = result.scalars().all()
        
        return [self._to_entity(db_task) for db_task in db_tasks]
    
    async def delete(self, task_id: UUID) -> bool:
        """
        Elimina una tarea por ID.
        
        Args:
            task_id: UUID de la tarea
            
        Returns:
            True si se eliminó, False si no existía
        """
        stmt = select(TaskModel).where(TaskModel.id == task_id)
        result = await self._session.execute(stmt)
        db_task = result.scalar_one_or_none()
        
        if db_task is None:
            return False
        
        await self._session.delete(db_task)
        await self._session.flush()
        
        return True
    
    async def exists(self, task_id: UUID) -> bool:
        """
        Verifica si existe una tarea.
        
        Args:
            task_id: UUID de la tarea
            
        Returns:
            True si existe
        """
        stmt = select(func.count()).select_from(TaskModel).where(
            TaskModel.id == task_id
        )
        result = await self._session.execute(stmt)
        count = result.scalar()
        
        return count > 0
    
    async def count(
        self,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        assigned_to: Optional[UUID] = None
    ) -> int:
        """
        Cuenta tareas que cumplen los criterios.
        
        Returns:
            Número de tareas
        """
        stmt = select(func.count()).select_from(TaskModel)
        
        if status is not None:
            stmt = stmt.where(TaskModel.status == status.value)
        
        if priority is not None:
            stmt = stmt.where(TaskModel.priority == priority.value)
        
        if assigned_to is not None:
            stmt = stmt.where(TaskModel.assigned_to == assigned_to)
        
        result = await self._session.execute(stmt)
        return result.scalar()
    
    async def find_by_assigned_user(
        self,
        user_id: UUID,
        status: Optional[Status] = None
    ) -> List[Task]:
        """
        Busca tareas asignadas a un usuario.
        
        Args:
            user_id: UUID del usuario
            status: Filtrar por estado (opcional)
            
        Returns:
            Lista de tareas asignadas
        """
        stmt = select(TaskModel).where(TaskModel.assigned_to == user_id)
        
        if status is not None:
            stmt = stmt.where(TaskModel.status == status.value)
        
        stmt = stmt.order_by(TaskModel.created_at.desc())
        
        result = await self._session.execute(stmt)
        db_tasks = result.scalars().all()
        
        return [self._to_entity(db_task) for db_task in db_tasks]
    
    # ============= MÉTODOS DE MAPEO =============
    
    def _to_entity(self, model: TaskModel) -> Task:
        """
        Convierte modelo de BD a entidad de dominio.
        
        Args:
            model: Modelo SQLAlchemy
            
        Returns:
            Entidad Task
        """
        return Task(
            task_id=model.id,
            title=model.title,
            description=model.description,
            priority=Priority(model.priority),
            status=Status(model.status),
            assigned_to=model.assigned_to,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at
        )
    
    def _to_model(self, entity: Task) -> TaskModel:
        """
        Convierte entidad de dominio a modelo de BD.
        
        Args:
            entity: Entidad Task
            
        Returns:
            Modelo SQLAlchemy
        """
        return TaskModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            priority=entity.priority.value,
            status=entity.status.value,
            assigned_to=entity.assigned_to,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            completed_at=entity.completed_at
        )
    
    def _update_model_from_entity(
        self,
        model: TaskModel,
        entity: Task
    ) -> None:
        """
        Actualiza un modelo existente con datos de la entidad.
        
        Args:
            model: Modelo a actualizar
            entity: Entidad con nuevos datos
        """
        model.title = entity.title
        model.description = entity.description
        model.priority = entity.priority.value
        model.status = entity.status.value
        model.assigned_to = entity.assigned_to
        model.updated_at = entity.updated_at
        model.completed_at = entity.completed_at
