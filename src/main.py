"""
FastAPI Application - Entry Point
Configuración principal de la aplicación
"""
import sys
from pathlib import Path

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from src.infrastructure.api.routes import tasks, health, auth
from src.infrastructure.api.middleware.error_handler import (
    domain_exception_handler,
    general_exception_handler
)
from src.infrastructure.api.middleware.logging_middleware import LoggingMiddleware
from src.infrastructure.database.connection import init_db, close_db
from src.infrastructure.config.settings import get_settings
from src.infrastructure.logging.logger import setup_logging
from src.domain.exceptions.task_exceptions import DomainException


# Agregar el directorio raíz al PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Configurar logging
setup_logging()

# Obtener configuración
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Gestiona el ciclo de vida de la aplicación.
    Ejecuta código al inicio y al cierre.
    """
    # Startup
    print("🚀 Starting Task Management API...")
    await init_db()
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down Task Management API...")
    await close_db()
    print("✅ Database connections closed")


# Crear aplicación FastAPI
app = FastAPI(
    title="Task Management API",
    description="API REST para gestión de tareas con arquitectura hexagonal",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)


# ============= MIDDLEWARE =============

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Logging personalizado
app.add_middleware(LoggingMiddleware)


# ============= EXCEPTION HANDLERS =============

# Manejador para excepciones de dominio
app.add_exception_handler(DomainException, domain_exception_handler)

# Manejador para excepciones generales
app.add_exception_handler(Exception, general_exception_handler)

# Manejador para errores de validación de Pydantic
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """Maneja errores de validación de Pydantic"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "body": exc.body
        }
    )


# ============= ROUTERS =============

# Incluir routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(tasks.router)


# ============= ROOT ENDPOINT =============

@app.get(
    "/",
    tags=["root"],
    summary="Root endpoint",
    response_model=dict
)
async def root() -> dict:
    """
    Endpoint raíz que proporciona información básica de la API.
    """
    return {
        "message": "Task Management API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/api/health"
    }


# ============= STARTUP MESSAGE =============

@app.on_event("startup")
async def startup_message():
    """Mensaje de inicio"""
    print(f"""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        🎯 Task Management API - Running                  ║
    ║                                                          ║
    ║        Environment: {settings.ENVIRONMENT:<20}           ║
    ║        Docs:        {settings.API_HOST}/api/docs         ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)


# Para ejecutar con uvicorn directamente
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level="info"
    )
