from passlib.context import CryptContext


class PasswordHasher:
    """
    Servicio para manejo seguro de contraseñas.
    
    Usa bcrypt para hashing, que es resistente a:
    - Rainbow table attacks
    - Brute force attacks (debido a su lentitud intencional)
    """
    
    def __init__(self):
        # Configurar contexto de bcrypt
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=12  # Factor de trabajo (más alto = más seguro pero más lento)
        )
    
    def hash_password(self, password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña
            
        Example:
            hasher = PasswordHasher()
            hashed = hasher.hash_password("my_password123")
            # Retorna: $2b$12$KIXxkj...
        """
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash almacenado
            
        Returns:
            True si la contraseña es correcta, False en caso contrario
            
        Example:
            hasher = PasswordHasher()
            is_valid = hasher.verify_password(
                "my_password123",
                stored_hash
            )
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Verifica si un hash necesita ser actualizado.
        
        Útil cuando se cambia el factor de trabajo (rounds).
        
        Args:
            hashed_password: Hash a verificar
            
        Returns:
            True si el hash debe ser actualizado
            
        Example:
            if hasher.needs_rehash(user.password_hash):
                user.password_hash = hasher.hash_password(plain_password)
        """
        return self.pwd_context.needs_update(hashed_password)
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Valida la fortaleza de una contraseña.
        
        Criterios:
        - Mínimo 8 caracteres
        - Al menos una mayúscula
        - Al menos una minúscula
        - Al menos un número
        - Al menos un carácter especial
        
        Args:
            password: Contraseña a validar
            
        Returns:
            Tupla (es_válida, mensaje_error)
            
        Example:
            valid, message = hasher.validate_password_strength("weak")
            if not valid:
                raise ValueError(message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is strong"
