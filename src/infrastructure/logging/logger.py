"""
Logging Configuration
Configuración centralizada de logging para toda la aplicación
"""
import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

from ..config.settings import get_settings


settings = get_settings()


def add_app_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: EventDict
) -> EventDict:
    """
    Agrega contexto de la aplicación a cada log.
    
    Args:
        logger: Logger instance
        method_name: Nombre del método de logging
        event_dict: Diccionario del evento
        
    Returns:
        Event dict con contexto agregado
    """
    event_dict["app"] = "task-management-api"
    event_dict["environment"] = settings.ENVIRONMENT
    return event_dict


def setup_logging() -> None:
    """
    Configura el sistema de logging de la aplicación.
    
    Usa structlog para logs estructurados en JSON (producción)
    o formato legible (desarrollo).
    """
    # Configurar el nivel de logging
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    # Procesadores compartidos
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_app_context,
        structlog.processors.StackInfoRenderer(),
    ]
    
    # Procesadores específicos según entorno
    if settings.LOG_FORMAT == "json" or settings.is_production:
        # Producción: JSON estructurado
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]
    else:
        # Desarrollo: formato legible con colores
        processors = shared_processors + [
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    
    # Configurar structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configurar logging estándar de Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # Configurar loggers de librerías externas
    logging.getLogger("uvicorn").setLevel(log_level)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.is_development else logging.WARNING
    )
    
    # Log inicial
    logger = structlog.get_logger(__name__)
    logger.info(
        "logging_configured",
        log_level=settings.LOG_LEVEL,
        log_format=settings.LOG_FORMAT,
        environment=settings.ENVIRONMENT,
    )


def get_logger(name: str) -> Any:
    """
    Obtiene un logger estructurado para un módulo específico.
    
    Args:
        name: Nombre del módulo (típicamente __name__)
        
    Returns:
        Logger configurado
        
    Usage:
        logger = get_logger(__name__)
        logger.info("message", key="value")
    """
    return structlog.get_logger(name)


# ============= Configuración de logs para desarrollo =============

class ColoredFormatter(logging.Formatter):
    """
    Formatter con colores para logs en desarrollo.
    Alternativa simple a structlog dev renderer.
    """
    
    # Códigos de color ANSI
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m',      # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Formatea el log con colores"""
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']
        
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


# ============= Filtros de logging =============

class HealthCheckFilter(logging.Filter):
    """
    Filtro para excluir logs de health checks (reduce ruido).
    """
    
    def filter(self, record: logging.LogRecord) -> bool:
        """
        Retorna False si el log es de un health check.
        
        Args:
            record: Log record
            
        Returns:
            True si debe loggearse, False si debe filtrarse
        """
        message = record.getMessage()
        return "/health" not in message and "/api/health" not in message


# ============= Decorador para logging de funciones =============

def log_function_call(logger_name: str = __name__):
    """
    Decorador que loggea la entrada y salida de una función.
    
    Args:
        logger_name: Nombre del logger a usar
        
    Usage:
        @log_function_call()
        async def my_function(arg1, arg2):
            ...
    """
    def decorator(func):
        logger = get_logger(logger_name)
        
        async def async_wrapper(*args, **kwargs):
            logger.debug(
                f"calling_{func.__name__}",
                function=func.__name__,
                args=args,
                kwargs=kwargs,
            )
            
            try:
                result = await func(*args, **kwargs)
                logger.debug(
                    f"completed_{func.__name__}",
                    function=func.__name__,
                )
                return result
            except Exception as e:
                logger.error(
                    f"failed_{func.__name__}",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            logger.debug(
                f"calling_{func.__name__}",
                function=func.__name__,
                args=args,
                kwargs=kwargs,
            )
            
            try:
                result = func(*args, **kwargs)
                logger.debug(
                    f"completed_{func.__name__}",
                    function=func.__name__,
                )
                return result
            except Exception as e:
                logger.error(
                    f"failed_{func.__name__}",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise
        
        # Retornar wrapper apropiado según si es async o sync
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
