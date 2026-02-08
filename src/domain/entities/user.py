from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


class User:
    """
    Entidad User con encapsulación de lógica de negocio.
    Representa un usuario del sistema.
    """
    
    def __init__(
        self,
        email: str,
        username: str,
        hashed_password: str,
        user_id: Optional[UUID] = None,
        is_active: bool = True,
        is_verified: bool = False,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        last_login: Optional[datetime] = None
    ):
        self._id = user_id or uuid4()
        self._email = ""
        self._username = ""
        self._hashed_password = hashed_password
        self._is_active = is_active
        self._is_verified = is_verified
        self._created_at = created_at or datetime.utcnow()
        self._updated_at = updated_at or datetime.utcnow()
        self._last_login = last_login
        
        # Validaciones en construcción
        self.set_email(email)
        self.set_username(username)
    
    # ============= GETTERS =============
    
    @property
    def id(self) -> UUID:
        return self._id
    
    @property
    def email(self) -> str:
        return self._email
    
    @property
    def username(self) -> str:
        return self._username
    
    @property
    def hashed_password(self) -> str:
        return self._hashed_password
    
    @property
    def is_active(self) -> bool:
        return self._is_active
    
    @property
    def is_verified(self) -> bool:
        return self._is_verified
    
    @property
    def created_at(self) -> datetime:
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        return self._updated_at
    
    @property
    def last_login(self) -> Optional[datetime]:
        return self._last_login
    
    # ============= COMPORTAMIENTO (Lógica de Negocio) =============
    
    def set_email(self, email: str) -> None:
        """Valida y establece el email"""
        if not email or len(email.strip()) == 0:
            raise ValueError("Email cannot be empty")
        
        email = email.strip().lower()
        
        # Validación básica de formato email
        if "@" not in email or "." not in email.split("@")[1]:
            raise ValueError("Invalid email format")
        
        if len(email) > 255:
            raise ValueError("Email cannot exceed 255 characters")
        
        self._email = email
        self._mark_as_updated()
    
    def set_username(self, username: str) -> None:
        """Valida y establece el username"""
        if not username or len(username.strip()) == 0:
            raise ValueError("Username cannot be empty")
        
        username = username.strip()
        
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        
        if len(username) > 50:
            raise ValueError("Username cannot exceed 50 characters")
        
        # Solo permite letras, números, guiones y guiones bajos
        if not all(c.isalnum() or c in ["-", "_"] for c in username):
            raise ValueError("Username can only contain letters, numbers, hyphens and underscores")
        
        self._username = username
        self._mark_as_updated()
    
    def change_password(self, new_hashed_password: str) -> None:
        """
        Cambia la contraseña del usuario.
        
        Args:
            new_hashed_password: Hash de la nueva contraseña
        """
        if not new_hashed_password:
            raise ValueError("Password hash cannot be empty")
        
        self._hashed_password = new_hashed_password
        self._mark_as_updated()
    
    def activate(self) -> None:
        """Activa el usuario"""
        if self._is_active:
            return  # Idempotente
        
        self._is_active = True
        self._mark_as_updated()
    
    def deactivate(self) -> None:
        """Desactiva el usuario"""
        if not self._is_active:
            return  # Idempotente
        
        self._is_active = False
        self._mark_as_updated()
    
    def verify(self) -> None:
        """Marca el usuario como verificado"""
        if self._is_verified:
            return  # Idempotente
        
        self._is_verified = True
        self._mark_as_updated()
    
    def record_login(self) -> None:
        """Registra el último login del usuario"""
        if not self._is_active:
            raise ValueError("Cannot login as inactive user")
        
        self._last_login = datetime.utcnow()
        self._mark_as_updated()
    
    # ============= CONSULTAS (Query Methods) =============
    
    def can_login(self) -> bool:
        """Verifica si el usuario puede iniciar sesión"""
        return self._is_active
    
    def needs_verification(self) -> bool:
        """Verifica si el usuario necesita verificación"""
        return not self._is_verified
    
    def has_logged_in(self) -> bool:
        """Verifica si el usuario ha iniciado sesión alguna vez"""
        return self._last_login is not None
    
    # ============= MÉTODOS PRIVADOS =============
    
    def _mark_as_updated(self) -> None:
        """Actualiza el timestamp de modificación"""
        self._updated_at = datetime.utcnow()
    
    # ============= MÉTODOS MÁGICOS =============
    
    def __eq__(self, other: object) -> bool:
        """Dos usuarios son iguales si tienen el mismo ID"""
        if not isinstance(other, User):
            return False
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash basado en el ID"""
        return hash(self._id)
    
    def __repr__(self) -> str:
        return (
            f"User(id={self._id}, username='{self._username}', "
            f"email='{self._email}', is_active={self._is_active})"
        )
