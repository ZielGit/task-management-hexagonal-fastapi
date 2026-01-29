import pytest
from uuid import uuid4, UUID

from src.domain.value_objects.priority import Priority
from src.domain.value_objects.status import Status
from src.domain.value_objects.task_id import TaskId


# ============= TESTS DE PRIORITY =============

class TestPriority:
    """Tests del Value Object Priority"""
    
    def test_priority_values(self):
        """Debe tener los 4 valores correctos"""
        assert Priority.LOW.value == "low"
        assert Priority.MEDIUM.value == "medium"
        assert Priority.HIGH.value == "high"
        assert Priority.URGENT.value == "urgent"
    
    def test_priority_from_string_valid(self):
        """Debe crear Priority desde string válido"""
        assert Priority.from_string("low") == Priority.LOW
        assert Priority.from_string("medium") == Priority.MEDIUM
        assert Priority.from_string("high") == Priority.HIGH
        assert Priority.from_string("urgent") == Priority.URGENT
    
    def test_priority_from_string_case_insensitive(self):
        """Debe aceptar strings en cualquier case"""
        assert Priority.from_string("LOW") == Priority.LOW
        assert Priority.from_string("Medium") == Priority.MEDIUM
        assert Priority.from_string("HIGH") == Priority.HIGH
        assert Priority.from_string("URGENT") == Priority.URGENT
    
    def test_priority_from_string_invalid(self):
        """Debe rechazar strings inválidos"""
        with pytest.raises(ValueError, match="Invalid priority"):
            Priority.from_string("invalid")
        
        with pytest.raises(ValueError, match="Invalid priority"):
            Priority.from_string("super_urgent")
    
    def test_priority_is_critical(self):
        """Debe identificar prioridades críticas"""
        assert Priority.HIGH.is_critical()
        assert Priority.URGENT.is_critical()
        assert not Priority.MEDIUM.is_critical()
        assert not Priority.LOW.is_critical()
    
    def test_priority_string_representation(self):
        """Debe tener representación string correcta"""
        assert str(Priority.LOW) == "low"
        assert str(Priority.MEDIUM) == "medium"
        assert str(Priority.HIGH) == "high"
        assert str(Priority.URGENT) == "urgent"
    
    def test_priority_comparison(self):
        """Debe poder comparar prioridades"""
        assert Priority.LOW == Priority.LOW
        assert Priority.HIGH != Priority.LOW
        assert Priority.URGENT != Priority.MEDIUM


# ============= TESTS DE STATUS =============

class TestStatus:
    """Tests del Value Object Status"""
    
    def test_status_values(self):
        """Debe tener los 4 estados correctos"""
        assert Status.TODO.value == "todo"
        assert Status.IN_PROGRESS.value == "in_progress"
        assert Status.DONE.value == "done"
        assert Status.CANCELLED.value == "cancelled"
    
    def test_status_from_string_valid(self):
        """Debe crear Status desde string válido"""
        assert Status.from_string("todo") == Status.TODO
        assert Status.from_string("in_progress") == Status.IN_PROGRESS
        assert Status.from_string("done") == Status.DONE
        assert Status.from_string("cancelled") == Status.CANCELLED
    
    def test_status_from_string_case_insensitive(self):
        """Debe aceptar strings en cualquier case"""
        assert Status.from_string("TODO") == Status.TODO
        assert Status.from_string("In_Progress") == Status.IN_PROGRESS
        assert Status.from_string("DONE") == Status.DONE
        assert Status.from_string("CANCELLED") == Status.CANCELLED
    
    def test_status_from_string_invalid(self):
        """Debe rechazar strings inválidos"""
        with pytest.raises(ValueError, match="Invalid status"):
            Status.from_string("invalid")
        
        with pytest.raises(ValueError, match="Invalid status"):
            Status.from_string("pending")
    
    def test_status_is_terminal(self):
        """Debe identificar estados terminales"""
        assert Status.DONE.is_terminal()
        assert Status.CANCELLED.is_terminal()
        assert not Status.TODO.is_terminal()
        assert not Status.IN_PROGRESS.is_terminal()
    
    def test_status_is_active(self):
        """Debe identificar estados activos"""
        assert Status.TODO.is_active()
        assert Status.IN_PROGRESS.is_active()
        assert not Status.DONE.is_active()
        assert not Status.CANCELLED.is_active()
    
    def test_status_string_representation(self):
        """Debe tener representación string correcta"""
        assert str(Status.TODO) == "todo"
        assert str(Status.IN_PROGRESS) == "in_progress"
        assert str(Status.DONE) == "done"
        assert str(Status.CANCELLED) == "cancelled"
    
    def test_status_comparison(self):
        """Debe poder comparar estados"""
        assert Status.TODO == Status.TODO
        assert Status.DONE != Status.TODO
        assert Status.IN_PROGRESS != Status.CANCELLED


# ============= TESTS DE TASK_ID =============

class TestTaskId:
    """Tests del Value Object TaskId"""
    
    def test_create_from_uuid(self):
        """Debe crear TaskId desde UUID"""
        uuid = uuid4()
        task_id = TaskId(uuid)
        
        assert task_id.value == uuid
        assert isinstance(task_id.value, UUID)
    
    def test_create_from_string(self):
        """Debe crear TaskId desde string UUID válido"""
        uuid_str = str(uuid4())
        task_id = TaskId(uuid_str)
        
        assert isinstance(task_id.value, UUID)
        assert str(task_id.value) == uuid_str
    
    def test_create_from_invalid_string(self):
        """Debe rechazar strings UUID inválidos"""
        with pytest.raises(ValueError, match="Invalid UUID format"):
            TaskId("invalid-uuid")
        
        with pytest.raises(ValueError, match="Invalid UUID format"):
            TaskId("12345")
    
    def test_create_from_invalid_type(self):
        """Debe rechazar tipos inválidos"""
        with pytest.raises(TypeError, match="TaskId must be str or UUID"):
            TaskId(123)
        
        with pytest.raises(TypeError, match="TaskId must be str or UUID"):
            TaskId([])
    
    def test_generate_new_task_id(self):
        """Debe generar TaskId único"""
        task_id1 = TaskId.generate()
        task_id2 = TaskId.generate()
        
        assert isinstance(task_id1, TaskId)
        assert isinstance(task_id2, TaskId)
        assert task_id1 != task_id2
        assert isinstance(task_id1.value, UUID)
    
    def test_task_id_equality(self):
        """Debe comparar TaskIds correctamente"""
        uuid = uuid4()
        task_id1 = TaskId(uuid)
        task_id2 = TaskId(uuid)
        task_id3 = TaskId(uuid4())
        
        assert task_id1 == task_id2
        assert task_id1 != task_id3
        assert task_id2 != task_id3
    
    def test_task_id_hash(self):
        """Debe ser hasheable para usar en sets/dicts"""
        uuid = uuid4()
        task_id1 = TaskId(uuid)
        task_id2 = TaskId(uuid)
        
        # Mismo UUID debe tener mismo hash
        assert hash(task_id1) == hash(task_id2)
        
        # Debe poder usar en set
        task_id_set = {task_id1, task_id2}
        assert len(task_id_set) == 1  # Son el mismo ID
    
    def test_task_id_can_be_used_in_set(self):
        """Debe poder usarse en sets"""
        task_id1 = TaskId.generate()
        task_id2 = TaskId.generate()
        task_id3 = TaskId(task_id1.value)  # Mismo UUID que task_id1
        
        task_set = {task_id1, task_id2, task_id3}
        
        assert len(task_set) == 2  # task_id1 y task_id3 son el mismo
        assert task_id1 in task_set
        assert task_id2 in task_set
    
    def test_task_id_can_be_used_as_dict_key(self):
        """Debe poder usarse como key en diccionarios"""
        task_id1 = TaskId.generate()
        task_id2 = TaskId.generate()
        
        task_dict = {
            task_id1: "Task 1",
            task_id2: "Task 2"
        }
        
        assert task_dict[task_id1] == "Task 1"
        assert task_dict[task_id2] == "Task 2"
    
    def test_task_id_string_representation(self):
        """Debe tener representación string correcta"""
        uuid = uuid4()
        task_id = TaskId(uuid)
        
        assert str(task_id) == str(uuid)
    
    def test_task_id_repr(self):
        """Debe tener __repr__ útil para debugging"""
        uuid = uuid4()
        task_id = TaskId(uuid)
        
        repr_str = repr(task_id)
        assert "TaskId" in repr_str
        assert str(uuid) in repr_str


# ============= TESTS DE INMUTABILIDAD =============

class TestValueObjectImmutability:
    """Tests para verificar inmutabilidad de Value Objects"""
    
    def test_priority_is_immutable(self):
        """Priority debe ser inmutable (enum)"""
        priority = Priority.HIGH
        
        # No se puede modificar el valor
        with pytest.raises(AttributeError):
            priority.value = "super_high"
    
    def test_status_is_immutable(self):
        """Status debe ser inmutable (enum)"""
        status = Status.IN_PROGRESS
        
        # No se puede modificar el valor
        with pytest.raises(AttributeError):
            status.value = "almost_done"
    
    def test_task_id_value_is_immutable(self):
        """TaskId.value debe ser inmutable"""
        task_id = TaskId.generate()
        original_value = task_id.value
        
        # Intentar modificar el valor no debería afectar el original
        # (UUID es inmutable por naturaleza)
        with pytest.raises(AttributeError):
            task_id.value = uuid4()
        
        assert task_id.value == original_value


# ============= TESTS DE EDGE CASES =============

class TestValueObjectEdgeCases:
    """Tests de casos extremos"""
    
    def test_priority_with_whitespace(self):
        """Debe manejar strings con espacios"""
        # El método from_string usa .lower() que maneja espacios
        with pytest.raises(ValueError):
            Priority.from_string("  high  ")
    
    def test_status_with_whitespace(self):
        """Debe manejar strings con espacios"""
        with pytest.raises(ValueError):
            Status.from_string("  done  ")
    
    def test_task_id_from_empty_string(self):
        """Debe rechazar string vacío"""
        with pytest.raises(ValueError):
            TaskId("")
    
    def test_task_id_from_none(self):
        """Debe rechazar None"""
        with pytest.raises(TypeError):
            TaskId(None)


# ============= TESTS DE INTEGRACIÓN ENTRE VALUE OBJECTS =============

class TestValueObjectsIntegration:
    """Tests de cómo interactúan los value objects"""
    
    def test_can_use_all_value_objects_together(self):
        """Debe poder usar todos los value objects juntos"""
        task_id = TaskId.generate()
        priority = Priority.HIGH
        status = Status.TODO
        
        # Simular datos de una tarea
        task_data = {
            "id": task_id,
            "priority": priority,
            "status": status
        }
        
        assert task_data["id"] == task_id
        assert task_data["priority"] == Priority.HIGH
        assert task_data["status"] == Status.TODO
    
    def test_value_objects_in_collections(self):
        """Debe poder usar value objects en colecciones"""
        priorities = [Priority.LOW, Priority.MEDIUM, Priority.HIGH]
        statuses = {Status.TODO, Status.IN_PROGRESS, Status.DONE}
        task_ids = {
            TaskId.generate(): "Task 1",
            TaskId.generate(): "Task 2"
        }
        
        assert len(priorities) == 3
        assert len(statuses) == 3
        assert len(task_ids) == 2
