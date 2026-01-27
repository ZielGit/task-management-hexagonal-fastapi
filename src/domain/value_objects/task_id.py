from uuid import UUID, uuid4
from typing import Union


class TaskId:
    """
    Value Object para el ID de tarea.
    Encapsula validación y conversión.
    """
    
    def __init__(self, value: Union[str, UUID]):
        if isinstance(value, str):
            try:
                self._value = UUID(value)
            except ValueError:
                raise ValueError(f"Invalid UUID format: {value}")
        elif isinstance(value, UUID):
            self._value = value
        else:
            raise TypeError(f"TaskId must be str or UUID, got {type(value)}")
    
    @classmethod
    def generate(cls) -> "TaskId":
        """Genera un nuevo TaskId único"""
        return cls(uuid4())
    
    @property
    def value(self) -> UUID:
        return self._value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TaskId):
            return False
        return self._value == other._value
    
    def __hash__(self) -> int:
        return hash(self._value)
    
    def __str__(self) -> str:
        return str(self._value)
    
    def __repr__(self) -> str:
        return f"TaskId({self._value})"
