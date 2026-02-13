import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.infrastructure.database.models import Base
from src.infrastructure.database.connection import get_db_session


# ============= ENGINE EN MEMORIA =============

@pytest_asyncio.fixture(scope="session")
async def e2e_engine():
    """
    Engine SQLite en memoria con StaticPool.
    StaticPool garantiza que todas las conexiones comparten
    la misma conexión física y ven los mismos datos.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
def e2e_session_factory(e2e_engine):
    """Factory de sesiones para la sesión e2e."""
    return async_sessionmaker(
        bind=e2e_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


# ============= OVERRIDE DE DEPENDENCIA =============

@pytest_asyncio.fixture(scope="function")
async def override_db(e2e_session_factory):
    """
    Reemplaza get_db_session con una sesión que hace commit
    automático al finalizar cada request. Esto es necesario
    porque register y login usan sesiones distintas — sin commit
    la segunda sesión no ve los datos escritos por la primera.
    """
    async def _get_test_db():
        async with e2e_session_factory() as session:
            try:
                yield session
                await session.commit()   # commit explícito tras cada request
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = _get_test_db
    yield
    app.dependency_overrides.pop(get_db_session, None)


# ============= CLIENT =============

@pytest_asyncio.fixture(scope="function")
async def client(override_db):
    """Cliente HTTP con BD en memoria y commit automático activo."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
