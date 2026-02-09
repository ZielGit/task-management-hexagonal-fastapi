from typing import Dict, Any
from uuid import UUID

from ...application.ports.auth_service import AuthService
from .jwt_service import JWTService
from .password_hasher import PasswordHasher


class AuthServiceImpl(AuthService):
    """
    Implementación concreta del AuthService usando JWT y bcrypt.
    """
    
    def __init__(self):
        self._jwt_service = JWTService()
        self._password_hasher = PasswordHasher()
    
    def hash_password(self, password: str) -> str:
        """Hashea una contraseña usando bcrypt"""
        return self._password_hasher.hash_password(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return self._password_hasher.verify_password(plain_password, hashed_password)
    
    def create_access_token(self, user_id: UUID, email: str) -> str:
        """Crea un token JWT de acceso"""
        return self._jwt_service.create_access_token(
            data={
                "sub": str(user_id),
                "email": email
            }
        )
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """Decodifica y valida un token JWT"""
        return self._jwt_service.decode_token(token)
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Valida la fortaleza de una contraseña"""
        return self._password_hasher.validate_password_strength(password)
