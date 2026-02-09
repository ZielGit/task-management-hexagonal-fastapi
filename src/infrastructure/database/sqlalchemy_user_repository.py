from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from .models import UserModel


class SQLAlchemyUserRepository(UserRepository):
    """
    Implementación del repositorio de usuarios usando SQLAlchemy.
    Traduce entre entidades de dominio y modelos de BD.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Args:
            session: Sesión de SQLAlchemy para operaciones de BD
        """
        self._session = session
    
    async def save(self, user: User) -> User:
        """
        Persiste un usuario (insert o update).
        
        Args:
            user: Entidad User del dominio
            
        Returns:
            El usuario persistido
        """
        # Buscar si ya existe
        stmt = select(UserModel).where(UserModel.id == user.id)
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user:
            # UPDATE: actualizar modelo existente
            self._update_model_from_entity(db_user, user)
        else:
            # INSERT: crear nuevo modelo
            db_user = self._to_model(user)
            self._session.add(db_user)
        
        await self._session.flush()
        await self._session.refresh(db_user)
        
        return self._to_entity(db_user)
    
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Busca un usuario por ID.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user is None:
            return None
        
        return self._to_entity(db_user)
    
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por email.
        
        Args:
            email: Email del usuario (case-insensitive)
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        stmt = select(UserModel).where(
            UserModel.email == email.lower().strip()
        )
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user is None:
            return None
        
        return self._to_entity(db_user)
    
    async def find_by_username(self, username: str) -> Optional[User]:
        """
        Busca un usuario por username.
        
        Args:
            username: Username del usuario
            
        Returns:
            Entidad User si existe, None en caso contrario
        """
        stmt = select(UserModel).where(
            UserModel.username == username.strip()
        )
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user is None:
            return None
        
        return self._to_entity(db_user)
    
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado.
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe
        """
        stmt = select(UserModel.id).where(
            UserModel.email == email.lower().strip()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def exists_by_username(self, username: str) -> bool:
        """
        Verifica si existe un usuario con el username dado.
        
        Args:
            username: Username a verificar
            
        Returns:
            True si existe
        """
        stmt = select(UserModel.id).where(
            UserModel.username == username.strip()
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def delete(self, user_id: UUID) -> bool:
        """
        Elimina un usuario por ID.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            True si se eliminó, False si no existía
        """
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        db_user = result.scalar_one_or_none()
        
        if db_user is None:
            return False
        
        await self._session.delete(db_user)
        await self._session.flush()
        
        return True
    
    # ============= MÉTODOS DE MAPEO =============
    
    def _to_entity(self, model: UserModel) -> User:
        """
        Convierte modelo de BD a entidad de dominio.
        
        Args:
            model: Modelo SQLAlchemy
            
        Returns:
            Entidad User
        """
        return User(
            user_id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            is_verified=model.is_verified if hasattr(model, 'is_verified') else False,
            created_at=model.created_at,
            updated_at=model.updated_at if hasattr(model, 'updated_at') else model.created_at,
            last_login=model.last_login if hasattr(model, 'last_login') else None
        )
    
    def _to_model(self, entity: User) -> UserModel:
        """
        Convierte entidad de dominio a modelo de BD.
        
        Args:
            entity: Entidad User
            
        Returns:
            Modelo SQLAlchemy
        """
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login=entity.last_login
        )
    
    def _update_model_from_entity(
        self,
        model: UserModel,
        entity: User
    ) -> None:
        """
        Actualiza un modelo existente con datos de la entidad.
        
        Args:
            model: Modelo a actualizar
            entity: Entidad con nuevos datos
        """
        model.email = entity.email
        model.username = entity.username
        model.hashed_password = entity.hashed_password
        model.is_active = entity.is_active
        
        if hasattr(model, 'is_verified'):
            model.is_verified = entity.is_verified
        if hasattr(model, 'updated_at'):
            model.updated_at = entity.updated_at
        if hasattr(model, 'last_login'):
            model.last_login = entity.last_login
