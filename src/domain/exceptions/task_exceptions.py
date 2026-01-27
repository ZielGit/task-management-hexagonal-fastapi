class DomainException(Exception):
    """Base para todas las excepciones del dominio"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TaskException(DomainException):
    """Base para excepciones relacionadas con Task"""
    pass


class TaskNotFoundException(TaskException):
    """Se lanza cuando no se encuentra una tarea"""
    
    def __init__(self, task_id: str):
        super().__init__(f"Task with id {task_id} not found")
        self.task_id = task_id


class InvalidTaskStateTransition(TaskException):
    """Se lanza cuando se intenta una transición de estado inválida"""
    pass


class TaskAlreadyCompleted(TaskException):
    """Se lanza cuando se intenta modificar una tarea completada"""
    pass


class TaskNotAssignable(TaskException):
    """Se lanza cuando una tarea no puede ser asignada"""
    pass


class TaskValidationError(TaskException):
    """Se lanza cuando los datos de la tarea no son válidos"""
    pass


class TaskDeletionNotAllowed(TaskException):
    """Se lanza cuando una tarea no puede ser eliminada"""
    
    def __init__(self, task_id: str, reason: str):
        super().__init__(
            f"Task {task_id} cannot be deleted: {reason}"
        )
        self.task_id = task_id
        self.reason = reason


class UserNotFoundException(DomainException):
    """Se lanza cuando no se encuentra un usuario"""
    
    def __init__(self, user_id: str):
        super().__init__(f"User with id {user_id} not found")
        self.user_id = user_id


class UnauthorizedOperationException(DomainException):
    """Se lanza cuando un usuario intenta una operación no autorizada"""
    
    def __init__(self, operation: str, user_id: str):
        super().__init__(
            f"User {user_id} is not authorized to perform: {operation}"
        )
        self.operation = operation
        self.user_id = user_id
