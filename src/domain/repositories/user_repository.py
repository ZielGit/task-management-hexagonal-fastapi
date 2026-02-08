from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from ..entities.user import User


class UserRepository(ABC):
    """
    Interface del repositorio de User (Puerto).
    La capa de dominio define QUÉ necesita, no CÓMO se implementa.
    """
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """
        Persiste un usuario nuevo o actualiza uno existente.
        
        Args:
            user: Entidad User a persistir
            
        Returns:
            El usuario persistido
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Busca un usuario por su ID.
        
        Args:
            user_id: UUID del usuario
            
        Returns:
            El usuario si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            El usuario si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[User]:
        """
        Busca un usuario por su username.
        
        Args:
            username: Username del usuario
            
        Returns:
            El usuario si existe, None en caso contrario
        """
        pass
    
    @abstractmethod
    async def exists_by_email(self, email: str) -> bool:
        """
        Verifica si existe un usuario con el email dado.
        
        Args:
            email: Email a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def exists_by_username(self, username: str) -> bool:
        """
        Verifica si existe un usuario con el username dado.
        
        Args:
            username: Username a verificar
            
        Returns:
            True si existe, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Elimina un usuario por su ID.
        
        Args:
            user_id: UUID del usuario a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        pass
