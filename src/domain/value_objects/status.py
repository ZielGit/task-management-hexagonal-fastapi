from enum import Enum

class Status(str, Enum):
    """
    Enumeración de estados de tarea.
    Value Object inmutable.
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"
    
    @classmethod
    def from_string(cls, value: str) -> "Status":
        """Crea Status desde string con validación"""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid status: {value}. "
                f"Valid options: {', '.join([s.value for s in cls])}"
            )
    
    def is_terminal(self) -> bool:
        """Verifica si el estado es terminal (no puede cambiar fácilmente)"""
        return self in [Status.DONE, Status.CANCELLED]
    
    def is_active(self) -> bool:
        """Verifica si la tarea está activa"""
        return self in [Status.TODO, Status.IN_PROGRESS]
    
    def __str__(self) -> str:
        return self.value