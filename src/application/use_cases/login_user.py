from ...domain.repositories.user_repository import UserRepository
from ...application.ports.auth_service import AuthService
from ..dtos.user_dto import LoginUserDTO, TokenResponseDTO


class LoginUserUseCase:
    """
    Caso de uso para autenticar un usuario.
    """
    
    def __init__(
        self,
        user_repository: UserRepository,
        auth_service: AuthService
    ):
        self._user_repository = user_repository
        self._auth_service = auth_service
    
    async def execute(self, dto: LoginUserDTO) -> TokenResponseDTO:
        """
        Autentica un usuario y genera un token JWT.
        
        Args:
            dto: Credenciales de login (email/password)
            
        Returns:
            DTO con el token de acceso
            
        Raises:
            ValueError: Si las credenciales son inválidas
        """
        # 1. Buscar usuario por email
        user = await self._user_repository.find_by_email(dto.email)
        
        if user is None:
            raise ValueError("Invalid email or password")
        
        # 2. Verificar que el usuario está activo
        if not user.can_login():
            raise ValueError("User account is inactive")
        
        # 3. Verificar contraseña
        is_valid = self._auth_service.verify_password(
            dto.password,
            user.hashed_password
        )
        
        if not is_valid:
            raise ValueError("Invalid email or password")
        
        # 4. Registrar login
        user.record_login()
        await self._user_repository.save(user)
        
        # 5. Generar token JWT
        token = self._auth_service.create_access_token(
            user_id=user.id,
            email=user.email
        )
        
        # 6. Retornar token
        from ...infrastructure.config.settings import get_settings
        settings = get_settings()
        
        return TokenResponseDTO(
            access_token=token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60
        )
