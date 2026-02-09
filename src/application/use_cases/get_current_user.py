from uuid import UUID

from ...domain.repositories.user_repository import UserRepository
from ..dtos.user_dto import UserResponseDTO


class GetCurrentUserUseCase:
    """
    Caso de uso para obtener información del usuario actual.
    """
    
    def __init__(self, user_repository: UserRepository):
        self._user_repository = user_repository
    
    async def execute(self, user_id: UUID) -> UserResponseDTO:
        """
        Obtiene la información del usuario actual.
        
        Args:
            user_id: UUID del usuario autenticado
            
        Returns:
            DTO con los datos del usuario
            
        Raises:
            ValueError: Si el usuario no existe
        """
        user = await self._user_repository.find_by_id(user_id)
        
        if user is None:
            raise ValueError("User not found")
        
        return UserResponseDTO(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            created_at=user.created_at
        )
