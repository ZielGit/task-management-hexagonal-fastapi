from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ....application.use_cases.register_user import RegisterUserUseCase
from ....application.use_cases.login_user import LoginUserUseCase
from ....application.use_cases.get_current_user import GetCurrentUserUseCase
from ....application.dtos.user_dto import (
    RegisterUserDTO,
    LoginUserDTO,
    UserResponseDTO,
    TokenResponseDTO
)
from ..dependencies import (
    get_register_user_use_case,
    get_login_user_use_case,
    get_current_user_use_case,
    get_current_user_id
)


router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)

security = HTTPBearer()


# ============= Endpoints =============

@router.post(
    "/register",
    response_model=UserResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user in the system",
    responses={
        201: {"description": "User registered successfully"},
        400: {"description": "Invalid input or user already exists"},
        422: {"description": "Validation error"}
    }
)
async def register(
    user_data: RegisterUserDTO,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case)
) -> UserResponseDTO:
    """
    Registra un nuevo usuario en el sistema.
    
    - **email**: Email único del usuario
    - **username**: Username único (3-50 caracteres)
    - **password**: Contraseña segura (mínimo 8 caracteres)
    
    La contraseña debe contener:
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    - Al menos un carácter especial
    """
    try:
        return await use_case.execute(user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}"
        )


@router.post(
    "/login",
    response_model=TokenResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate a user and return JWT token",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid credentials"},
        422: {"description": "Validation error"}
    }
)
async def login(
    credentials: LoginUserDTO,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case)
) -> TokenResponseDTO:
    """
    Autentica un usuario y retorna un token JWT.
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    
    El token debe incluirse en requests subsecuentes en el header:
    `Authorization: Bearer <token>`
    """
    try:
        return await use_case.execute(credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@router.get(
    "/me",
    response_model=UserResponseDTO,
    summary="Get current user",
    description="Get the currently authenticated user's information",
    responses={
        200: {"description": "User information retrieved"},
        401: {"description": "Not authenticated or invalid token"}
    }
)
async def get_current_user(
    user_id = Depends(get_current_user_id),
    use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case)
) -> UserResponseDTO:
    """
    Obtiene información del usuario autenticado actual.
    
    Requiere token JWT válido en el header Authorization.
    """
    try:
        return await use_case.execute(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving user: {str(e)}"
        )


@router.post(
    "/refresh",
    response_model=TokenResponseDTO,
    summary="Refresh token",
    description="Refresh an existing JWT token"
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenResponseDTO:
    """
    Refresca un token JWT existente.
    
    Requiere un token JWT válido actual.
    Retorna un nuevo token con tiempo de expiración extendido.
    """
    from ...auth.jwt_service import JWTService
    from ...config.settings import get_settings
    
    jwt_service = JWTService()
    settings = get_settings()
    
    try:
        # Verificar token actual
        payload = jwt_service.decode_token(credentials.credentials)
        
        # Crear nuevo token con los mismos datos
        new_token = jwt_service.create_access_token(
            data={"sub": payload.get("sub"), "email": payload.get("email")}
        )
        
        return TokenResponseDTO(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
