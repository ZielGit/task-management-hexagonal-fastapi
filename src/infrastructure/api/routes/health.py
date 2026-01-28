from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, status
from pydantic import BaseModel

from ...database.connection import check_db_health
from ...config.settings import get_settings


router = APIRouter(
    prefix="/api",
    tags=["health"]
)

settings = get_settings()


class HealthResponse(BaseModel):
    """Modelo de respuesta para health check"""
    status: str
    timestamp: datetime
    version: str
    environment: str
    database: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-27T10:30:00Z",
                "version": "1.0.0",
                "environment": "production",
                "database": "connected"
            }
        }


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check endpoint",
    description="Returns the health status of the API and its dependencies"
)
async def health_check() -> HealthResponse:
    """
    Verifica el estado de salud de la aplicación.
    
    Returns:
        HealthResponse con el estado del sistema
    """
    # Verificar conexión a base de datos
    db_status = "connected" if await check_db_health() else "disconnected"
    
    # Determinar estado general
    overall_status = "healthy" if db_status == "connected" else "unhealthy"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        database=db_status
    )


@router.get(
    "/health/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness check",
    description="Indicates if the application is ready to accept traffic"
)
async def readiness_check() -> Dict[str, Any]:
    """
    Verifica si la aplicación está lista para recibir tráfico.
    Útil para Kubernetes readiness probes.
    
    Returns:
        Dict con estado de readiness
    """
    db_ready = await check_db_health()
    
    if not db_ready:
        return {
            "ready": False,
            "reason": "Database not available"
        }
    
    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/live",
    status_code=status.HTTP_200_OK,
    summary="Liveness check",
    description="Indicates if the application is alive"
)
async def liveness_check() -> Dict[str, str]:
    """
    Verifica si la aplicación está viva.
    Útil para Kubernetes liveness probes.
    
    Returns:
        Dict indicando que la app está viva
    """
    return {
        "alive": "true",
        "timestamp": datetime.utcnow().isoformat()
    }
