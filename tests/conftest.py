import pytest
import asyncio
from typing import AsyncGenerator, Generator
from uuid import uuid4

# Para tests async
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

# Imports del proyecto
from src.infrastructure.database.models import Base
from src.domain.entities.task import Task
from src.domain.value_objects.priority import Priority
from src.domain.value_objects.status import Status


# ============= CONFIGURACIÓN DE PYTEST =============

def pytest_configure(config):
    """Configuración inicial de pytest"""
    # Registrar markers personalizados
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests (deselect with '-m \"not unit\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )


# ============= EVENT LOOP FIXTURE =============

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an instance of the default event loop for the test session.
    Necesario para tests async con pytest-asyncio.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ============= DATABASE FIXTURES =============

@pytest.fixture(scope="function")
async def test_db_engine():
    """
    Crea un engine de base de datos en memoria para tests.
    Cada test tiene su propia BD limpia.
    """
    # Usar SQLite en memoria para tests rápidos
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,  # No mostrar SQL en tests
        poolclass=NullPool,
    )
    
    # Crear todas las tablas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup: cerrar conexiones
    await engine.dispose()


@pytest.fixture(scope="function")
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Proporciona una sesión de BD para tests.
    Se hace rollback automático después de cada test.
    """
    # Crear session factory
    async_session = async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    async with async_session() as session:
        # Comenzar transacción
        async with session.begin():
            yield session
            # Rollback automático al salir


# ============= ENTITY FIXTURES =============

@pytest.fixture
def sample_task() -> Task:
    """
    Crea una tarea de ejemplo para tests.
    """
    return Task(
        title="Sample Task",
        description="This is a sample task for testing",
        priority=Priority.MEDIUM,
        status=Status.TODO
    )


@pytest.fixture
def urgent_task() -> Task:
    """
    Crea una tarea urgente para tests.
    """
    return Task(
        title="Urgent Task",
        description="This needs immediate attention",
        priority=Priority.URGENT,
        status=Status.TODO
    )


@pytest.fixture
def completed_task() -> Task:
    """
    Crea una tarea completada para tests.
    """
    task = Task(
        title="Completed Task",
        description="This task is already done",
        priority=Priority.HIGH,
        status=Status.TODO
    )
    task.start()
    task.complete()
    return task


@pytest.fixture
def cancelled_task() -> Task:
    """
    Crea una tarea cancelada para tests.
    """
    task = Task(
        title="Cancelled Task",
        description="This task was cancelled",
        priority=Priority.LOW,
        status=Status.TODO
    )
    task.cancel()
    return task


@pytest.fixture
def assigned_task() -> Task:
    """
    Crea una tarea asignada a un usuario.
    """
    task = Task(
        title="Assigned Task",
        description="This task is assigned",
        priority=Priority.MEDIUM,
        status=Status.TODO
    )
    task.assign_to(uuid4())
    return task


# ============= USER FIXTURES =============

@pytest.fixture
def user_id() -> str:
    """
    Genera un UUID de usuario para tests.
    """
    return uuid4()


@pytest.fixture
def another_user_id() -> str:
    """
    Genera otro UUID de usuario para tests.
    """
    return uuid4()


# ============= DTO FIXTURES =============

@pytest.fixture
def create_task_dto():
    """
    DTO válido para crear tarea.
    """
    from src.application.dtos.task_dto import CreateTaskDTO
    
    return CreateTaskDTO(
        title="Test Task",
        description="Test Description",
        priority=Priority.MEDIUM,
        auto_assign=False
    )


# ============= MOCK FIXTURES =============

@pytest.fixture
def mock_task_repository():
    """
    Mock del TaskRepository para tests unitarios.
    """
    from unittest.mock import AsyncMock
    
    repository = AsyncMock()
    
    # Configurar comportamientos por defecto
    async def mock_save(task: Task) -> Task:
        return task
    
    async def mock_find_by_id(task_id):
        return None
    
    repository.save = AsyncMock(side_effect=mock_save)
    repository.find_by_id = AsyncMock(side_effect=mock_find_by_id)
    repository.delete = AsyncMock(return_value=True)
    repository.find_all = AsyncMock(return_value=[])
    repository.count = AsyncMock(return_value=0)
    
    return repository


# ============= HELPERS =============

@pytest.fixture
def task_factory():
    """
    Factory para crear múltiples tareas con diferentes configuraciones.
    """
    def _create_task(
        title: str = "Test Task",
        description: str = "Test Description",
        priority: Priority = Priority.MEDIUM,
        status: Status = Status.TODO,
        assigned_to: str = None
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status
        )
        if assigned_to:
            task.assign_to(assigned_to)
        return task
    
    return _create_task


# ============= CLEANUP =============

@pytest.fixture(autouse=True)
def reset_singletons():
    """
    Reset de singletons entre tests para evitar estado compartido.
    Se ejecuta automáticamente antes de cada test.
    """
    # Aquí puedes resetear cualquier singleton o estado global
    # Por ejemplo:
    # from src.infrastructure.database.connection import engine, async_session_factory
    # engine = None
    # async_session_factory = None
    
    yield
    
    # Cleanup después del test si es necesario
