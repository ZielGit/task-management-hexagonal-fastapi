import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.entities.task import Task
from src.domain.value_objects.priority import Priority
from src.domain.value_objects.status import Status
from src.domain.exceptions.task_exceptions import (
    InvalidTaskStateTransition,
    TaskAlreadyCompleted,
    TaskNotAssignable
)


class TestTaskCreation:
    """Tests de creación de Task"""
    
    def test_create_task_with_valid_data(self):
        """Debe crear una tarea válida con datos correctos"""
        # Arrange & Act
        task = Task(
            title="Test Task",
            description="Test Description",
            priority=Priority.HIGH
        )
        
        # Assert
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == Priority.HIGH
        assert task.status == Status.TODO
        assert task.id is not None
        assert task.assigned_to is None
        assert isinstance(task.created_at, datetime)
    
    def test_create_task_validates_empty_title(self):
        """Debe rechazar títulos vacíos"""
        # Act & Assert
        with pytest.raises(ValueError, match="cannot be empty"):
            Task(
                title="",
                description="Test",
                priority=Priority.LOW
            )
    
    def test_create_task_validates_title_length(self):
        """Debe rechazar títulos demasiado largos"""
        # Arrange
        long_title = "x" * 201
        
        # Act & Assert
        with pytest.raises(ValueError, match="cannot exceed 200"):
            Task(
                title=long_title,
                description="Test",
                priority=Priority.LOW
            )
    
    def test_create_task_strips_whitespace(self):
        """Debe eliminar espacios en blanco del título"""
        # Act
        task = Task(
            title="  Test Task  ",
            description="  Test Description  ",
            priority=Priority.MEDIUM
        )
        
        # Assert
        assert task.title == "Test Task"
        assert task.description == "Test Description"


class TestTaskPriorityChange:
    """Tests de cambio de prioridad"""
    
    def test_change_priority_successfully(self):
        """Debe cambiar la prioridad de una tarea activa"""
        # Arrange
        task = Task("Task", "Description", Priority.LOW)
        
        # Act
        task.change_priority(Priority.URGENT)
        
        # Assert
        assert task.priority == Priority.URGENT
    
    def test_cannot_change_priority_of_completed_task(self):
        """No debe cambiar prioridad de tarea completada"""
        # Arrange
        task = Task("Task", "Description", Priority.LOW)
        task.start()
        task.complete()
        
        # Act & Assert
        with pytest.raises(TaskAlreadyCompleted):
            task.change_priority(Priority.HIGH)


class TestTaskStatusTransitions:
    """Tests de transiciones de estado"""
    
    def test_start_task_from_todo(self):
        """Debe iniciar una tarea en estado TODO"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        
        # Act
        task.start()
        
        # Assert
        assert task.status == Status.IN_PROGRESS
    
    def test_cannot_start_task_already_in_progress(self):
        """No debe reiniciar una tarea en progreso"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.start()
        
        # Act & Assert
        with pytest.raises(InvalidTaskStateTransition):
            task.start()
    
    def test_complete_task_from_in_progress(self):
        """Debe completar una tarea en progreso"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.start()
        
        # Act
        task.complete()
        
        # Assert
        assert task.status == Status.DONE
        assert task.completed_at is not None
        assert task.is_completed()
    
    def test_cannot_complete_cancelled_task(self):
        """No debe completar una tarea cancelada"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.cancel()
        
        # Act & Assert
        with pytest.raises(InvalidTaskStateTransition):
            task.complete()
    
    def test_cancel_task(self):
        """Debe cancelar una tarea activa"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        
        # Act
        task.cancel()
        
        # Assert
        assert task.status == Status.CANCELLED
        assert task.is_cancelled()
    
    def test_reopen_completed_task(self):
        """Debe reabrir una tarea completada"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.start()
        task.complete()
        
        # Act
        task.reopen()
        
        # Assert
        assert task.status == Status.TODO
        assert task.completed_at is None
        assert not task.is_completed()


class TestTaskAssignment:
    """Tests de asignación de tareas"""
    
    def test_assign_task_to_user(self):
        """Debe asignar una tarea a un usuario"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        user_id = uuid4()
        
        # Act
        task.assign_to(user_id)
        
        # Assert
        assert task.assigned_to == user_id
        assert task.is_assigned()
    
    def test_cannot_assign_completed_task(self):
        """No debe asignar una tarea completada"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.start()
        task.complete()
        user_id = uuid4()
        
        # Act & Assert
        with pytest.raises(TaskNotAssignable):
            task.assign_to(user_id)
    
    def test_unassign_task(self):
        """Debe desasignar una tarea"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        user_id = uuid4()
        task.assign_to(user_id)
        
        # Act
        task.unassign()
        
        # Assert
        assert task.assigned_to is None
        assert not task.is_assigned()


class TestTaskDeletion:
    """Tests de lógica de eliminación"""
    
    def test_cancelled_task_can_be_deleted(self):
        """Una tarea cancelada puede ser eliminada"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.cancel()
        
        # Assert
        assert task.can_be_deleted()
    
    def test_active_task_cannot_be_deleted(self):
        """Una tarea activa no puede ser eliminada"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        
        # Assert
        assert not task.can_be_deleted()
    
    def test_recently_completed_task_cannot_be_deleted(self):
        """Una tarea recién completada no puede ser eliminada"""
        # Arrange
        task = Task("Task", "Description", Priority.MEDIUM)
        task.start()
        task.complete()
        
        # Assert
        assert not task.can_be_deleted()


class TestTaskQueries:
    """Tests de métodos de consulta"""
    
    def test_is_high_priority(self):
        """Debe identificar tareas de alta prioridad"""
        # Arrange
        high_task = Task("Task", "Description", Priority.HIGH)
        urgent_task = Task("Task", "Description", Priority.URGENT)
        medium_task = Task("Task", "Description", Priority.MEDIUM)
        
        # Assert
        assert high_task.is_high_priority()
        assert urgent_task.is_high_priority()
        assert not medium_task.is_high_priority()


class TestTaskEquality:
    """Tests de igualdad entre tareas"""
    
    def test_tasks_with_same_id_are_equal(self):
        """Tareas con el mismo ID son iguales"""
        # Arrange
        task_id = uuid4()
        task1 = Task("Task 1", "Desc 1", Priority.LOW, task_id=task_id)
        task2 = Task("Task 2", "Desc 2", Priority.HIGH, task_id=task_id)
        
        # Assert
        assert task1 == task2
    
    def test_tasks_with_different_ids_are_not_equal(self):
        """Tareas con diferentes IDs no son iguales"""
        # Arrange
        task1 = Task("Task 1", "Desc 1", Priority.LOW)
        task2 = Task("Task 1", "Desc 1", Priority.LOW)
        
        # Assert
        assert task1 != task2
    
    def test_task_can_be_used_in_set(self):
        """Tareas pueden usarse en sets (requiere __hash__)"""
        # Arrange
        task1 = Task("Task 1", "Desc 1", Priority.LOW)
        task2 = Task("Task 2", "Desc 2", Priority.HIGH)
        
        # Act
        task_set = {task1, task2}
        
        # Assert
        assert len(task_set) == 2
        assert task1 in task_set
