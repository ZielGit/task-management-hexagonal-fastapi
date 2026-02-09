from abc import ABC, abstractmethod
from typing import Dict, Any
from uuid import UUID


class AuthService(ABC):
    """
    Interface del servicio de autenticación.
    Define el contrato para operaciones de autenticación.
    """
    
    @abstractmethod
    def hash_password(self, password: str) -> str:
        """
        Hashea una contraseña.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
        """
        pass
    
    @abstractmethod
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash almacenado
            
        Returns:
            True si la contraseña es correcta
        """
        pass
    
    @abstractmethod
    def create_access_token(self, user_id: UUID, email: str) -> str:
        """
        Crea un token de acceso JWT.
        
        Args:
            user_id: ID del usuario
            email: Email del usuario
            
        Returns:
            Token JWT codificado
        """
        pass
    
    @abstractmethod
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodifica y valida un token JWT.
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Diccionario con los datos del payload
            
        Raises:
            Exception: Si el token es inválido o ha expirado
        """
        pass
    
    @abstractmethod
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña.
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tupla (es_válida, mensaje)
        """
        pass
