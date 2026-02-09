from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator


# ============= INPUT DTOs =============

class RegisterUserDTO(BaseModel):
    """DTO para registrar un nuevo usuario"""
    
    email: EmailStr = Field(
        ...,
        description="User email address"
    )
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username"
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User password (min 8 characters)"
    )
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Valida que el username solo contenga caracteres permitidos"""
        if not v.strip():
            raise ValueError("Username cannot be empty or whitespace")
        
        v = v.strip()
        
        # Solo letras, números, guiones y guiones bajos
        if not all(c.isalnum() or c in ['-', '_'] for c in v):
            raise ValueError("Username can only contain letters, numbers, hyphens and underscores")
        
        return v
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "username": "john_doe",
                    "password": "SecurePass123!"
                }
            ]
        }
    }


class LoginUserDTO(BaseModel):
    """DTO para login de usuario"""
    
    email: EmailStr = Field(
        ...,
        description="User email"
    )
    password: str = Field(
        ...,
        description="User password"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "user@example.com",
                    "password": "SecurePass123!"
                }
            ]
        }
    }


# ============= OUTPUT DTOs =============

class UserResponseDTO(BaseModel):
    """DTO de respuesta con datos de usuario"""
    
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                    "username": "john_doe",
                    "is_active": True,
                    "is_verified": False,
                    "created_at": "2024-01-15T10:30:00Z"
                }
            ]
        }
    }


class TokenResponseDTO(BaseModel):
    """DTO de respuesta con token JWT"""
    
    access_token: str = Field(
        ...,
        description="JWT access token"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')"
    )
    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds"
    )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "expires_in": 86400
                }
            ]
        }
    }
