import pytest
from uuid import uuid4
from httpx import AsyncClient

from src.main import app
from src.domain.value_objects.priority import Priority
from src.domain.value_objects.status import Status


# Mock para autenticación (simplificado)
def get_mock_current_user_id():
    """Mock del usuario actual para tests"""
    return uuid4()


@pytest.fixture
async def client():
    """Fixture que provee un cliente HTTP de prueba"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def auth_headers():
    """Fixture que provee headers de autenticación mock"""
    # En un test real, aquí se generaría un JWT válido
    return {
        "Authorization": "Bearer fake-jwt-token-for-testing"
    }


@pytest.mark.asyncio
class TestCreateTaskEndpoint:
    """Tests del endpoint POST /api/v1/tasks"""
    
    async def test_create_task_success(self, client, auth_headers):
        """Debe crear una tarea exitosamente"""
        # Arrange
        payload = {
            "title": "Implement feature X",
            "description": "Add new feature to the system",
            "priority": "high",
            "auto_assign": False
        }
        
        # Act
        response = await client.post(
            "/api/v1/tasks/",
            json=payload,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Implement feature X"
        assert data["description"] == "Add new feature to the system"
        assert data["priority"] == "high"
        assert data["status"] == "todo"
        assert "id" in data
        assert "created_at" in data
    
    async def test_create_task_with_auto_assign(self, client, auth_headers):
        """Debe auto-asignar la tarea"""
        # Arrange
        payload = {
            "title": "Review code",
            "description": "Review PR #123",
            "priority": "medium",
            "auto_assign": True
        }
        
        # Act
        response = await client.post(
            "/api/v1/tasks/",
            json=payload,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["assigned_to"] is not None
    
    async def test_create_task_validation_error(self, client, auth_headers):
        """Debe rechazar datos inválidos"""
        # Arrange
        payload = {
            "title": "",  # Título vacío - inválido
            "description": "Test",
            "priority": "low"
        }
        
        # Act
        response = await client.post(
            "/api/v1/tasks/",
            json=payload,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity
    
    async def test_create_task_unauthorized(self, client):
        """Debe rechazar requests sin autenticación"""
        # Arrange
        payload = {
            "title": "Test task",
            "description": "Test",
            "priority": "low"
        }
        
        # Act
        response = await client.post(
            "/api/v1/tasks/",
            json=payload
            # Sin headers de autenticación
        )
        
        # Assert
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetTaskEndpoint:
    """Tests del endpoint GET /api/v1/tasks/{task_id}"""
    
    async def test_get_existing_task(self, client, auth_headers):
        """Debe obtener una tarea existente"""
        # Arrange - Primero crear una tarea
        create_payload = {
            "title": "Get test task",
            "description": "Task to be retrieved",
            "priority": "medium"
        }
        create_response = await client.post(
            "/api/v1/tasks/",
            json=create_payload,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Act
        response = await client.get(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == task_id
        assert data["title"] == "Get test task"
    
    async def test_get_nonexistent_task(self, client, auth_headers):
        """Debe retornar 404 para tarea inexistente"""
        # Arrange
        fake_id = uuid4()
        
        # Act
        response = await client.get(
            f"/api/v1/tasks/{fake_id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 404


@pytest.mark.asyncio
class TestListTasksEndpoint:
    """Tests del endpoint GET /api/v1/tasks"""
    
    async def test_list_tasks_without_filters(self, client, auth_headers):
        """Debe listar todas las tareas"""
        # Act
        response = await client.get(
            "/api/v1/tasks/",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert "total" in data
        assert "limit" in data
        assert "offset" in data
        assert isinstance(data["tasks"], list)
    
    async def test_list_tasks_with_status_filter(self, client, auth_headers):
        """Debe filtrar tareas por estado"""
        # Act
        response = await client.get(
            "/api/v1/tasks/?status=todo",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        for task in data["tasks"]:
            assert task["status"] == "todo"
    
    async def test_list_tasks_with_pagination(self, client, auth_headers):
        """Debe paginar resultados"""
        # Act
        response = await client.get(
            "/api/v1/tasks/?limit=10&offset=0",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 10
        assert data["offset"] == 0
        assert len(data["tasks"]) <= 10


@pytest.mark.asyncio
class TestUpdateTaskEndpoint:
    """Tests del endpoint PUT /api/v1/tasks/{task_id}"""
    
    async def test_update_task_title(self, client, auth_headers):
        """Debe actualizar el título de una tarea"""
        # Arrange - Crear tarea
        create_payload = {
            "title": "Original title",
            "description": "Description",
            "priority": "low"
        }
        create_response = await client.post(
            "/api/v1/tasks/",
            json=create_payload,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Act - Actualizar
        update_payload = {
            "title": "Updated title"
        }
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated title"
        assert data["description"] == "Description"  # No cambió
    
    async def test_update_task_status(self, client, auth_headers):
        """Debe actualizar el estado de una tarea"""
        # Arrange
        create_payload = {
            "title": "Task to update",
            "description": "Test",
            "priority": "medium"
        }
        create_response = await client.post(
            "/api/v1/tasks/",
            json=create_payload,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Act
        update_payload = {
            "status": "in_progress"
        }
        response = await client.put(
            f"/api/v1/tasks/{task_id}",
            json=update_payload,
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "in_progress"


@pytest.mark.asyncio
class TestDeleteTaskEndpoint:
    """Tests del endpoint DELETE /api/v1/tasks/{task_id}"""
    
    async def test_delete_cancelled_task(self, client, auth_headers):
        """Debe eliminar una tarea cancelada"""
        # Arrange - Crear y cancelar tarea
        create_payload = {
            "title": "Task to delete",
            "description": "Will be cancelled",
            "priority": "low"
        }
        create_response = await client.post(
            "/api/v1/tasks/",
            json=create_payload,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Cancelar la tarea
        await client.put(
            f"/api/v1/tasks/{task_id}",
            json={"status": "cancelled"},
            headers=auth_headers
        )
        
        # Act - Eliminar
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task deleted successfully"
        assert data["task_id"] == task_id
    
    async def test_cannot_delete_active_task(self, client, auth_headers):
        """No debe eliminar una tarea activa"""
        # Arrange
        create_payload = {
            "title": "Active task",
            "description": "Cannot be deleted",
            "priority": "high"
        }
        create_response = await client.post(
            "/api/v1/tasks/",
            json=create_payload,
            headers=auth_headers
        )
        task_id = create_response.json()["id"]
        
        # Act
        response = await client.delete(
            f"/api/v1/tasks/{task_id}",
            headers=auth_headers
        )
        
        # Assert
        assert response.status_code == 400  # Bad Request
