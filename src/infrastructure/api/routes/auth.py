from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field

from ...auth.jwt_service import JWTService
from ...auth.password_hasher import PasswordHasher
from ...config.settings import get_settings


router = APIRouter(
    prefix="/api/auth",
    tags=["authentication"]
)

settings = get_settings()
security = HTTPBearer()


# ============= DTOs =============

class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., min_length=8, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class RegisterRequest(BaseModel):
    """Request para registro"""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "username": "johndoe",
                "password": "SecurePass123!"
            }
        }


class TokenResponse(BaseModel):
    """Response con token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 86400
            }
        }


class UserResponse(BaseModel):
    """Response con datos de usuario"""
    id: str
    email: EmailStr
    username: str
    is_active: bool
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "email": "user@example.com",
                "username": "johndoe",
                "is_active": True
            }
        }


# ============= Endpoints =============

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate a user and return JWT token"
)
async def login(credentials: LoginRequest) -> TokenResponse:
    """
    Autentica un usuario y retorna un token JWT.
    
    Args:
        credentials: Email y password del usuario
        
    Returns:
        TokenResponse con el JWT
        
    Raises:
        HTTPException: Si las credenciales son inválidas
    """
    # TODO: Verificar credenciales contra la base de datos
    # Por ahora, implementación simplificada para demo
    
    # Simular validación (en producción: verificar contra BD)
    if credentials.email == "demo@example.com" and credentials.password == "demo123456":
        # Generar token
        jwt_service = JWTService()
        token = jwt_service.create_access_token(
            data={"sub": "demo-user-id", "email": credentials.email}
        )
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60
        )
    
    # Credenciales inválidas
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"}
    )


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Register a new user in the system"
)
async def register(user_data: RegisterRequest) -> UserResponse:
    """
    Registra un nuevo usuario en el sistema.
    
    Args:
        user_data: Datos del nuevo usuario
        
    Returns:
        UserResponse con los datos del usuario creado
        
    Raises:
        HTTPException: Si el email ya está registrado
    """
    # TODO: Implementar registro real contra base de datos
    # Por ahora, implementación simplificada
    
    # Simular verificación de email duplicado
    # En producción: verificar contra BD
    
    # Hash de la contraseña
    hasher = PasswordHasher()
    hashed_password = hasher.hash_password(user_data.password)
    
    # Simular creación de usuario
    # En producción: guardar en BD
    from uuid import uuid4
    
    return UserResponse(
        id=str(uuid4()),
        email=user_data.email,
        username=user_data.username,
        is_active=True
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get the currently authenticated user's information"
)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserResponse:
    """
    Obtiene información del usuario autenticado actual.
    
    Args:
        credentials: Token JWT del header Authorization
        
    Returns:
        UserResponse con datos del usuario
        
    Raises:
        HTTPException: Si el token es inválido
    """
    jwt_service = JWTService()
    
    try:
        # Decodificar token
        payload = jwt_service.decode_token(credentials.credentials)
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        # TODO: Obtener usuario de la base de datos
        # Por ahora, retornar datos del token
        return UserResponse(
            id=user_id,
            email=email,
            username="demo_user",
            is_active=True
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh token",
    description="Refresh an existing JWT token"
)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenResponse:
    """
    Refresca un token JWT existente.
    
    Args:
        credentials: Token JWT actual
        
    Returns:
        TokenResponse con nuevo token
    """
    jwt_service = JWTService()
    
    try:
        # Verificar token actual
        payload = jwt_service.decode_token(credentials.credentials)
        
        # Crear nuevo token con los mismos datos
        new_token = jwt_service.create_access_token(
            data={"sub": payload.get("sub"), "email": payload.get("email")}
        )
        
        return TokenResponse(
            access_token=new_token,
            token_type="bearer",
            expires_in=settings.JWT_EXPIRATION_MINUTES * 60
        )
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
