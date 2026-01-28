"""
Error Handler Middleware
Manejo centralizado de excepciones y conversión a respuestas HTTP
"""
import traceback
from typing import Union

from fastapi import Request, status
from fastapi.responses import JSONResponse

from ....domain.exceptions.task_exceptions import (
    DomainException,
    TaskNotFoundException,
    TaskValidationError,
    InvalidTaskStateTransition,
    TaskDeletionNotAllowed,
    TaskNotAssignable,
    TaskAlreadyCompleted,
    UserNotFoundException,
    UnauthorizedOperationException,
)


async def domain_exception_handler(
    request: Request,
    exc: DomainException
) -> JSONResponse:
    """
    Maneja excepciones del dominio y las convierte en respuestas HTTP apropiadas.
    
    Args:
        request: Request de FastAPI
        exc: Excepción del dominio
        
    Returns:
        JSONResponse con el error formateado
    """
    # Mapeo de excepciones de dominio a códigos HTTP
    status_code_mapping = {
        TaskNotFoundException: status.HTTP_404_NOT_FOUND,
        UserNotFoundException: status.HTTP_404_NOT_FOUND,
        TaskValidationError: status.HTTP_400_BAD_REQUEST,
        InvalidTaskStateTransition: status.HTTP_400_BAD_REQUEST,
        TaskDeletionNotAllowed: status.HTTP_400_BAD_REQUEST,
        TaskNotAssignable: status.HTTP_400_BAD_REQUEST,
        TaskAlreadyCompleted: status.HTTP_400_BAD_REQUEST,
        UnauthorizedOperationException: status.HTTP_403_FORBIDDEN,
    }
    
    # Obtener código de estado apropiado
    status_code = status_code_mapping.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    # Construir respuesta
    return JSONResponse(
        status_code=status_code,
        content={
            "error": type(exc).__name__,
            "message": str(exc),
            "detail": exc.message if hasattr(exc, 'message') else str(exc),
            "path": request.url.path,
        }
    )


async def general_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Maneja excepciones generales no capturadas.
    
    Args:
        request: Request de FastAPI
        exc: Excepción genérica
        
    Returns:
        JSONResponse con error 500
    """
    # Log del error completo (en producción esto iría a un servicio de logging)
    print(f"❌ Unhandled exception: {type(exc).__name__}")
    print(f"   Message: {str(exc)}")
    print(f"   Path: {request.url.path}")
    
    # En desarrollo, incluir traceback
    from ...config.settings import get_settings
    settings = get_settings()
    
    error_detail = {
        "error": "InternalServerError",
        "message": "An unexpected error occurred",
        "path": request.url.path,
    }
    
    # Solo en desarrollo: incluir detalles del error
    if settings.is_development:
        error_detail["detail"] = str(exc)
        error_detail["type"] = type(exc).__name__
        error_detail["traceback"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_detail
    )


# ============= Exception Handler para tipos específicos =============

async def validation_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Maneja errores de validación de Pydantic.
    Ya está definido en main.py, pero aquí está la versión completa.
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Invalid request data",
            "detail": str(exc),
            "path": request.url.path,
        }
    )


async def http_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    Maneja HTTPExceptions de FastAPI.
    """
    from fastapi import HTTPException
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": "HTTPException",
                "message": exc.detail,
                "path": request.url.path,
            },
            headers=exc.headers
        )
    
    # Si no es HTTPException, pasar a general handler
    return await general_exception_handler(request, exc)
