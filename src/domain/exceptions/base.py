class DomainException(Exception):
    """Base para todas las excepciones del dominio"""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
