from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    create_async_engine,
    async_sessionmaker
)
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool

from ..config.settings import get_settings
from .models import Base


settings = get_settings()

# Motor de base de datos (singleton)
engine: AsyncEngine | None = None

# Session factory
async_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """
    Obtiene o crea el engine de SQLAlchemy.
    
    Returns:
        AsyncEngine configurado
    """
    global engine
    
    if engine is None:
        # Configuración de pooling para async
        pool_config = {}
        
        # En testing, usar NullPool para evitar problemas
        if settings.ENVIRONMENT == "testing":
            pool_config["poolclass"] = NullPool
        else:
            # Para async engines, usar configuración específica
            pool_config = {
                "pool_size": settings.DB_POOL_SIZE,
                "max_overflow": settings.DB_MAX_OVERFLOW,
                "pool_timeout": settings.DB_POOL_TIMEOUT,
                "pool_recycle": settings.DB_POOL_RECYCLE,
                "pool_pre_ping": True,  # Verificar conexión antes de usar
            }
        
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.is_development,  # Log SQL en desarrollo
            future=True,
            **pool_config
        )
    
    return engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Obtiene o crea la session factory.
    
    Returns:
        Async session maker
    """
    global async_session_factory
    
    if async_session_factory is None:
        async_session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
        )
    
    return async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para obtener una sesión de BD en FastAPI.
    
    Yields:
        AsyncSession para operaciones de BD
        
    Usage:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db_session)):
            ...
    """
    factory = get_session_factory()
    
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Inicializa la base de datos.
    Crea todas las tablas si no existen (solo para desarrollo).
    
    NOTA: En producción, usar Alembic para migraciones.
    """
    engine = get_engine()
    
    # Solo en desarrollo: crear tablas automáticamente
    if settings.is_development:
        async with engine.begin() as conn:
            # Crear todas las tablas definidas en Base
            await conn.run_sync(Base.metadata.create_all)
            print("✅ Database tables created (development mode)")
    else:
        print("ℹ️  Production mode: use Alembic migrations")


async def close_db() -> None:
    """
    Cierra la conexión a la base de datos.
    Debe llamarse al shutdown de la aplicación.
    """
    global engine, async_session_factory
    
    if engine is not None:
        await engine.dispose()
        engine = None
        async_session_factory = None
        print("✅ Database connections closed")


# ============= Healthcheck =============

async def check_db_health() -> bool:
    """
    Verifica la salud de la conexión a la base de datos.
    
    Returns:
        True si la conexión está activa, False en caso contrario
    """
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception as e:
        print(f"❌ Database health check failed: {e}")
        return False
