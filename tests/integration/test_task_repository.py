import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock

from src.application.use_cases.create_task import CreateTaskUseCase
from src.application.dtos.task_dto import CreateTaskDTO
from src.domain.entities.task import Task
from src.domain.value_objects.priority import Priority
from src.domain.value_objects.status import Status
from src.domain.exceptions.task_exceptions import TaskValidationError


@pytest.fixture
def mock_task_repository():
    """Fixture que provee un mock del repositorio"""
    repository = AsyncMock()
    
    # Configurar comportamiento del mock para save()
    async def save_task(task: Task) -> Task:
        """Simula guardar y retornar la tarea"""
        return task
    
    repository.save = AsyncMock(side_effect=save_task)
    
    return repository


@pytest.fixture
def create_task_use_case(mock_task_repository):
    """Fixture que provee el caso de uso con el repositorio mockeado"""
    return CreateTaskUseCase(mock_task_repository)


@pytest.mark.asyncio
class TestCreateTaskUseCase:
    """Tests del caso de uso CreateTask"""
    
    async def test_create_task_successfully(
        self,
        create_task_use_case,
        mock_task_repository
    ):
        """Debe crear una tarea exitosamente"""
        # Arrange
        dto = CreateTaskDTO(
            title="Implement login",
            description="Add JWT authentication",
            priority=Priority.HIGH,
            auto_assign=False
        )
        user_id = uuid4()
        
        # Act
        result = await create_task_use_case.execute(dto, user_id)
        
        # Assert
        assert result.title == "Implement login"
        assert result.description == "Add JWT authentication"
        assert result.priority == Priority.HIGH
        assert result.status == Status.TODO
        assert result.assigned_to is None
        
        # Verificar que se llamó al repositorio
        mock_task_repository.save.assert_called_once()
    
    async def test_create_task_with_auto_assign(
        self,
        create_task_use_case,
        mock_task_repository
    ):
        """Debe auto-asignar la tarea al creador"""
        # Arrange
        dto = CreateTaskDTO(
            title="Review PR",
            description="Review pull request #123",
            priority=Priority.MEDIUM,
            auto_assign=True
        )
        user_id = uuid4()
        
        # Act
        result = await create_task_use_case.execute(dto, user_id)
        
        # Assert
        assert result.assigned_to == user_id
        mock_task_repository.save.assert_called_once()
    
    async def test_create_task_rejects_forbidden_words(
        self,
        create_task_use_case
    ):
        """Debe rechazar tareas con palabras prohibidas"""
        # Arrange
        dto = CreateTaskDTO(
            title="This is spam content",
            description="Buy now!",
            priority=Priority.LOW
        )
        user_id = uuid4()
        
        # Act & Assert
        with pytest.raises(TaskValidationError, match="forbidden words"):
            await create_task_use_case.execute(dto, user_id)
    
    async def test_urgent_task_requires_description(
        self,
        create_task_use_case
    ):
        """Tareas urgentes deben tener descripción"""
        # Arrange
        dto = CreateTaskDTO(
            title="Urgent task",
            description="",  # Descripción vacía
            priority=Priority.URGENT
        )
        user_id = uuid4()
        
        # Act & Assert
        with pytest.raises(
            TaskValidationError,
            match="Urgent tasks must have a description"
        ):
            await create_task_use_case.execute(dto, user_id)
    
    async def test_repository_failure_propagates_error(
        self,
        mock_task_repository
    ):
        """Errores del repositorio deben propagarse"""
        # Arrange
        mock_task_repository.save = AsyncMock(
            side_effect=Exception("Database error")
        )
        use_case = CreateTaskUseCase(mock_task_repository)
        
        dto = CreateTaskDTO(
            title="Test task",
            description="Test",
            priority=Priority.LOW
        )
        user_id = uuid4()
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            await use_case.execute(dto, user_id)


@pytest.mark.asyncio
class TestCreateTaskValidations:
    """Tests específicos de validaciones"""
    
    async def test_strips_whitespace_from_title(
        self,
        create_task_use_case
    ):
        """Debe eliminar espacios del título"""
        # Arrange
        dto = CreateTaskDTO(
            title="  Task with spaces  ",
            description="Test",
            priority=Priority.LOW
        )
        user_id = uuid4()
        
        # Act
        result = await create_task_use_case.execute(dto, user_id)
        
        # Assert
        assert result.title == "Task with spaces"
    
    async def test_default_priority_is_medium(
        self,
        create_task_use_case
    ):
        """Prioridad por defecto debe ser MEDIUM"""
        # Arrange
        dto = CreateTaskDTO(
            title="Default task",
            description="Test"
            # priority no especificado
        )
        user_id = uuid4()
        
        # Act
        result = await create_task_use_case.execute(dto, user_id)
        
        # Assert
        assert result.priority == Priority.MEDIUM


@pytest.mark.asyncio
class TestCreateTaskDTO:
    """Tests del DTO CreateTask"""
    
    def test_dto_validates_min_title_length(self):
        """DTO debe rechazar título vacío"""
        # Act & Assert
        with pytest.raises(ValueError):
            CreateTaskDTO(
                title="",
                description="Test",
                priority=Priority.LOW
            )
    
    def test_dto_validates_max_title_length(self):
        """DTO debe rechazar título muy largo"""
        # Arrange
        long_title = "x" * 201
        
        # Act & Assert
        with pytest.raises(ValueError):
            CreateTaskDTO(
                title=long_title,
                description="Test",
                priority=Priority.LOW
            )
    
    def test_dto_accepts_valid_data(self):
        """DTO debe aceptar datos válidos"""
        # Act
        dto = CreateTaskDTO(
            title="Valid task",
            description="Valid description",
            priority=Priority.HIGH,
            auto_assign=True
        )
        
        # Assert
        assert dto.title == "Valid task"
        assert dto.description == "Valid description"
        assert dto.priority == Priority.HIGH
        assert dto.auto_assign is True
