from uuid import UUID

from ...domain.entities.user import User
from ...domain.repositories.user_repository import UserRepository
from ...application.ports.auth_service import AuthService
from ..dtos.user_dto import RegisterUserDTO, UserResponseDTO


class RegisterUserUseCase:
    """
    Caso de uso para registrar un nuevo usuario.
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self._user_repository = user_repository
        self._auth_service = auth_service
    
    async def execute(self, dto: RegisterUserDTO) -> UserResponseDTO:
        """
        Registra un nuevo usuario en el sistema.
        
        Args:
            dto: Datos del usuario a registrar
            
        Returns:
            DTO con los datos del usuario registrado
            
        Raises:
            ValueError: Si el email o username ya existe
            ValueError: Si la contraseña no es suficientemente fuerte
        """
        # 1. Validar que email no existe
        if await self._user_repository.exists_by_email(dto.email):
            raise ValueError(f"Email {dto.email} is already registered")
        
        # 2. Validar que username no existe
        if await self._user_repository.exists_by_username(dto.username):
            raise ValueError(f"Username {dto.username} is already taken")
        
        # 3. Validar fortaleza de contraseña
        is_valid, message = self._auth_service.validate_password_strength(dto.password)
        if not is_valid:
            raise ValueError(message)
        
        # 4. Hashear contraseña
        hashed_password = self._auth_service.hash_password(dto.password)
        
        # 5. Crear entidad User
        user = User(
            email=dto.email,
            username=dto.username,
            hashed_password=hashed_password
        )
        
        # 6. Persistir usuario
        saved_user = await self._user_repository.save(user)
        
        # 7. Retornar DTO de respuesta
        return UserResponseDTO(
            id=str(saved_user.id),
            email=saved_user.email,
            username=saved_user.username,
            is_active=saved_user.is_active,
            is_verified=saved_user.is_verified,
            created_at=saved_user.created_at
        )
