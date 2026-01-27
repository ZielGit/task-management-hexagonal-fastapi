from enum import Enum

class Priority(str, Enum):
    """
    Enumeración de prioridades de tarea.
    Value Object inmutable.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    
    @classmethod
    def from_string(cls, value: str) -> "Priority":
        """Crea Priority desde string con validación"""
        try:
            return cls(value.lower())
        except ValueError:
            raise ValueError(
                f"Invalid priority: {value}. "
                f"Valid options: {', '.join([p.value for p in cls])}"
            )
    
    def is_critical(self) -> bool:
        """Determina si la prioridad es crítica"""
        return self in [Priority.HIGH, Priority.URGENT]
    
    def __str__(self) -> str:
        return self.value
    