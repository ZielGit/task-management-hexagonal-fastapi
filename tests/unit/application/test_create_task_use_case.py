import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

from src.application.use_cases.create_task import CreateTaskUseCase
from src.application.dtos.task_dto import CreateTaskDTO
from src.domain.entities.task import Task
from src.domain.value_objects.priority import Priority
from src.domain.value_objects.status import Status
from src.domain.exceptions.task_exceptions import TaskValidationError


class TestCreateTaskUseCase:
    """Tests unitarios del caso de uso CreateTask"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock del TaskRepository"""
        repository = AsyncMock()
        
        # Configurar comportamiento del save
        async def mock_save(task: Task) -> Task:
            # Simular que la tarea se guardó correctamente
            return task
        
        repository.save = AsyncMock(side_effect=mock_save)
        return repository
    
    @pytest.fixture
    def use_case(self, mock_repository):
        """Instancia del caso de uso con repository mockeado"""
        return CreateTaskUseCase(mock_repository)
    
    @pytest.fixture
    def valid_dto(self):
        """DTO válido para crear tarea"""
        return CreateTaskDTO(
            title="Test Task",
            description="Test Description",
            priority=Priority.MEDIUM,
            auto_assign=False
        )
    
    @pytest.fixture
    def user_id(self):
        """UUID de usuario de prueba"""
        return uuid4()
    
    # ============= TESTS DE HAPPY PATH =============
    
    @pytest.mark.asyncio
    async def test_create_task_successfully(
        self,
        use_case,
        mock_repository,
        valid_dto,
        user_id
    ):
        """Debe crear una tarea exitosamente"""
        # Act
        result = await use_case.execute(valid_dto, user_id)
        
        # Assert
        assert result.title == "Test Task"
        assert result.description == "Test Description"
        assert result.priority == Priority.MEDIUM
        assert result.status == Status.TODO
        assert result.assigned_to is None
        assert result.id is not None
        
        # Verificar que se llamó al repositorio
        mock_repository.save.assert_called_once()
        saved_task = mock_repository.save.call_args[0][0]
        assert isinstance(saved_task, Task)
    
    @pytest.mark.asyncio
    async def test_create_task_with_high_priority(
        self,
        use_case,
        mock_repository,
        user_id
    ):
        """Debe crear tarea con prioridad alta"""
        # Arrange
        dto = CreateTaskDTO(
            title="Urgent Task",
            description="Needs immediate attention",
            priority=Priority.HIGH,
            auto_assign=False
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.priority == Priority.HIGH
        assert result.title == "Urgent Task"
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_with_auto_assign(
        self,
        use_case,
        mock_repository,
        user_id
    ):
        """Debe auto-asignar tarea al creador"""
        # Arrange
        dto = CreateTaskDTO(
            title="My Task",
            description="I'll do this",
            priority=Priority.MEDIUM,
            auto_assign=True
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.assigned_to == user_id
        mock_repository.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_task_always_starts_as_todo(
        self,
        use_case,
        valid_dto,
        user_id
    ):
        """Nuevas tareas siempre deben estar en estado TODO"""
        # Act
        result = await use_case.execute(valid_dto, user_id)
        
        # Assert
        assert result.status == Status.TODO
    
    @pytest.mark.asyncio
    async def test_create_task_generates_unique_id(
        self,
        use_case,
        valid_dto,
        user_id
    ):
        """Debe generar ID único para cada tarea"""
        # Act
        result1 = await use_case.execute(valid_dto, user_id)
        result2 = await use_case.execute(valid_dto, user_id)
        
        # Assert
        assert result1.id != result2.id
    
    # ============= TESTS DE VALIDACIÓN =============
    
    @pytest.mark.asyncio
    async def test_create_task_rejects_forbidden_words(
        self,
        use_case,
        user_id
    ):
        """Debe rechazar tareas con palabras prohibidas en título"""
        # Arrange
        dto = CreateTaskDTO(
            title="This is spam content",
            description="Buy now!",
            priority=Priority.LOW
        )
        
        # Act & Assert
        with pytest.raises(TaskValidationError, match="forbidden words"):
            await use_case.execute(dto, user_id)
    
    @pytest.mark.asyncio
    async def test_create_urgent_task_requires_description(
        self,
        use_case,
        user_id
    ):
        """Tareas urgentes deben tener descripción"""
        # Arrange
        dto = CreateTaskDTO(
            title="Urgent task",
            description="",  # Vacía
            priority=Priority.URGENT
        )
        
        # Act & Assert
        with pytest.raises(
            TaskValidationError,
            match="Urgent tasks must have a description"
        ):
            await use_case.execute(dto, user_id)
    
    @pytest.mark.asyncio
    async def test_create_urgent_task_with_description_succeeds(
        self,
        use_case,
        user_id
    ):
        """Tareas urgentes con descripción deben crearse"""
        # Arrange
        dto = CreateTaskDTO(
            title="Urgent task",
            description="This is urgent because...",
            priority=Priority.URGENT
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.priority == Priority.URGENT
        assert result.description == "This is urgent because..."
    
    @pytest.mark.asyncio
    async def test_create_task_strips_whitespace(
        self,
        use_case,
        user_id
    ):
        """Debe eliminar espacios en blanco del título y descripción"""
        # Arrange
        dto = CreateTaskDTO(
            title="  Task with spaces  ",
            description="  Description with spaces  ",
            priority=Priority.LOW
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.title == "Task with spaces"
        assert result.description == "Description with spaces"
    
    # ============= TESTS DE ERRORES =============
    
    @pytest.mark.asyncio
    async def test_repository_error_propagates(
        self,
        mock_repository,
        valid_dto,
        user_id
    ):
        """Errores del repositorio deben propagarse"""
        # Arrange
        mock_repository.save = AsyncMock(
            side_effect=Exception("Database connection failed")
        )
        use_case = CreateTaskUseCase(mock_repository)
        
        # Act & Assert
        with pytest.raises(Exception, match="Database connection failed"):
            await use_case.execute(valid_dto, user_id)
    
    @pytest.mark.asyncio
    async def test_repository_called_with_correct_task(
        self,
        use_case,
        mock_repository,
        valid_dto,
        user_id
    ):
        """El repositorio debe recibir una entidad Task válida"""
        # Act
        await use_case.execute(valid_dto, user_id)
        
        # Assert
        mock_repository.save.assert_called_once()
        saved_task = mock_repository.save.call_args[0][0]
        
        assert isinstance(saved_task, Task)
        assert saved_task.title == valid_dto.title
        assert saved_task.description == valid_dto.description
        assert saved_task.priority == valid_dto.priority
    
    # ============= TESTS DE DIFERENTES PRIORIDADES =============
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("priority", [
        Priority.LOW,
        Priority.MEDIUM,
        Priority.HIGH,
        Priority.URGENT
    ])
    async def test_create_task_with_all_priorities(
        self,
        use_case,
        user_id,
        priority
    ):
        """Debe crear tareas con cualquier prioridad"""
        # Arrange
        dto = CreateTaskDTO(
            title=f"Task with {priority.value} priority",
            description="Test description for urgent task" if priority == Priority.URGENT else "Test",
            priority=priority
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.priority == priority
    
    # ============= TESTS DE EDGE CASES =============
    
    @pytest.mark.asyncio
    async def test_create_task_with_minimum_title_length(
        self,
        use_case,
        user_id
    ):
        """Debe aceptar título de longitud mínima"""
        # Arrange
        dto = CreateTaskDTO(
            title="A",  # 1 carácter
            description="Test",
            priority=Priority.LOW
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.title == "A"
    
    @pytest.mark.asyncio
    async def test_create_task_with_maximum_title_length(
        self,
        use_case,
        user_id
    ):
        """Debe aceptar título de longitud máxima"""
        # Arrange
        long_title = "A" * 200  # Máximo 200 caracteres
        dto = CreateTaskDTO(
            title=long_title,
            description="Test",
            priority=Priority.LOW
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.title == long_title
        assert len(result.title) == 200
    
    @pytest.mark.asyncio
    async def test_create_task_with_empty_description(
        self,
        use_case,
        user_id
    ):
        """Debe aceptar descripción vacía para tareas no urgentes"""
        # Arrange
        dto = CreateTaskDTO(
            title="Task without description",
            description="",
            priority=Priority.LOW
        )
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert
        assert result.description == ""
    
    @pytest.mark.asyncio
    async def test_create_task_preserves_timestamps(
        self,
        use_case,
        valid_dto,
        user_id
    ):
        """Debe mantener timestamps de creación"""
        # Act
        result = await use_case.execute(valid_dto, user_id)
        
        # Assert
        assert result.created_at is not None
        assert result.updated_at is not None
        assert result.completed_at is None  # Nueva tarea no completada
    
    # ============= TESTS DE MÚLTIPLES USUARIOS =============
    
    @pytest.mark.asyncio
    async def test_different_users_create_tasks(
        self,
        use_case,
        valid_dto
    ):
        """Diferentes usuarios pueden crear tareas"""
        # Arrange
        user1_id = uuid4()
        user2_id = uuid4()
        
        dto_with_assign = CreateTaskDTO(
            title="Task",
            description="Test",
            priority=Priority.LOW,
            auto_assign=True
        )
        
        # Act
        result1 = await use_case.execute(dto_with_assign, user1_id)
        result2 = await use_case.execute(dto_with_assign, user2_id)
        
        # Assert
        assert result1.assigned_to == user1_id
        assert result2.assigned_to == user2_id
        assert result1.id != result2.id


class TestCreateTaskUseCaseIntegration:
    """Tests de integración del caso de uso"""
    
    @pytest.mark.asyncio
    async def test_use_case_workflow(self):
        """Test del flujo completo del caso de uso"""
        # Arrange
        mock_repo = AsyncMock()
        mock_repo.save = AsyncMock(side_effect=lambda task: task)
        
        use_case = CreateTaskUseCase(mock_repo)
        
        dto = CreateTaskDTO(
            title="Integration Test Task",
            description="Testing the full workflow",
            priority=Priority.HIGH,
            auto_assign=True
        )
        user_id = uuid4()
        
        # Act
        result = await use_case.execute(dto, user_id)
        
        # Assert - Verificar todo el flujo
        assert result.title == "Integration Test Task"
        assert result.priority == Priority.HIGH
        assert result.status == Status.TODO
        assert result.assigned_to == user_id
        assert mock_repo.save.called
