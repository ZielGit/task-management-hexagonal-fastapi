"""
Logging Middleware
Registra todas las requests y responses de la API
"""
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

import structlog


logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware que registra información de cada request/response.
    
    Registra:
    - Request ID único
    - Método HTTP y path
    - Tiempo de procesamiento
    - Status code de respuesta
    - User agent
    - IP del cliente
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Generar ID único para la request
        request_id = str(uuid.uuid4())
        
        # Agregar request_id al state de la request
        request.state.request_id = request_id
        
        # Timestamp de inicio
        start_time = time.time()
        
        # Extraer información de la request
        method = request.method
        url = str(request.url)
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log de inicio de request
        logger.info(
            "request_started",
            request_id=request_id,
            method=method,
            path=path,
            url=url,
            client_ip=client_host,
            user_agent=user_agent,
        )
        
        # Procesar la request
        try:
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Agregar headers personalizados a la response
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            # Log de request completada
            logger.info(
                "request_completed",
                request_id=request_id,
                method=method,
                path=path,
                status_code=response.status_code,
                process_time=f"{process_time:.4f}s",
            )
            
            return response
            
        except Exception as exc:
            # Calcular tiempo incluso en caso de error
            process_time = time.time() - start_time
            
            # Log de error
            logger.error(
                "request_failed",
                request_id=request_id,
                method=method,
                path=path,
                error=str(exc),
                error_type=type(exc).__name__,
                process_time=f"{process_time:.4f}s",
            )
            
            # Re-lanzar la excepción para que sea manejada por error handlers
            raise


class RequestContextMiddleware(BaseHTTPMiddleware):
    """
    Middleware que agrega contexto estructurado a los logs.
    Útil para tracing distribuido.
    """
    
    async def dispatch(
        self,
        request: Request,
        call_next: Callable
    ) -> Response:
        # Extraer o generar correlation ID
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            str(uuid.uuid4())
        )
        
        # Bind del contexto a structlog
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
        )
        
        try:
            response = await call_next(request)
            response.headers["X-Correlation-ID"] = correlation_id
            return response
        finally:
            # Limpiar contexto
            structlog.contextvars.clear_contextvars()


# ============= Función auxiliar para extraer request_id =============

def get_request_id(request: Request) -> str:
    """
    Extrae el request_id del state de la request.
    
    Args:
        request: Request de FastAPI
        
    Returns:
        Request ID si existe, "unknown" si no
    """
    return getattr(request.state, "request_id", "unknown")
