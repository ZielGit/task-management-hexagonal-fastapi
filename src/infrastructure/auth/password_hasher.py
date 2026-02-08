import hashlib
import bcrypt


class PasswordHasher:
    """
    Servicio para manejo seguro de contraseñas.
    
    Usa bcrypt para hashing, que es resistente a:
    - Rainbow table attacks
    - Brute force attacks (debido a su lentitud intencional)
    
    IMPORTANTE: bcrypt tiene un límite de 72 bytes. Contraseñas más largas
    se hashean primero con SHA-256 para mantener toda la entropía.
    """
    
    def __init__(self):
        self.bcrypt_rounds = 12  # 2^12 = 4096 iteraciones
        self.max_password_bytes = 72
    
    def _prepare_password(self, password: str) -> bytes:
        """
        Prepara la contraseña para bcrypt.
        
        Si excede 72 bytes, la hashea con SHA-256 primero.
        
        Args:
            password: Contraseña original
            
        Returns:
            Contraseña preparada como bytes para bcrypt
        """
        password_bytes = password.encode('utf-8')
        
        if len(password_bytes) > self.max_password_bytes:
            # Para contraseñas largas, usar SHA-256 primero
            # Usamos hexdigest() para evitar bytes nulos que bcrypt podría
            # interpretar como terminador de string
            hash_obj = hashlib.sha256(password_bytes)
            # hexdigest() retorna 64 caracteres (32 bytes en hex)
            return hash_obj.hexdigest().encode('utf-8')
        
        return password_bytes
    
    def hash_password(self, password: str) -> str:
        """
        Hashea una contraseña usando bcrypt.
        
        Maneja automáticamente contraseñas de más de 72 bytes
        aplicando SHA-256 primero.
        
        Args:
            password: Contraseña en texto plano
            
        Returns:
            Hash de la contraseña como string
            
        Example:
            hasher = PasswordHasher()
            hashed = hasher.hash_password("my_password123")
            # Retorna: $2b$12$KIXxkj...
        """
        prepared_password = self._prepare_password(password)
        
        # Generar salt y hashear
        salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
        hashed = bcrypt.hashpw(prepared_password, salt)
        
        # bcrypt retorna bytes, convertir a string para almacenamiento
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verifica si una contraseña coincide con su hash.
        
        Maneja automáticamente contraseñas largas igual que hash_password.
        
        Args:
            plain_password: Contraseña en texto plano
            hashed_password: Hash almacenado (string)
            
        Returns:
            True si la contraseña es correcta, False en caso contrario
            
        Example:
            hasher = PasswordHasher()
            is_valid = hasher.verify_password(
                "my_password123",
                stored_hash
            )
        """
        prepared_password = self._prepare_password(plain_password)
        hashed_bytes = hashed_password.encode('utf-8')
        
        try:
            return bcrypt.checkpw(prepared_password, hashed_bytes)
        except ValueError:
            # Hash inválido
            return False
    
    def needs_rehash(self, hashed_password: str) -> bool:
        """
        Verifica si un hash necesita ser actualizado.
        
        Verifica si el número de rounds del hash es menor al configurado.
        El formato de bcrypt es: $2b$rounds$salthash
        donde rounds es el log2 del número de iteraciones (ej: 12 = 2^12 = 4096)
        
        Args:
            hashed_password: Hash a verificar
            
        Returns:
            True si el hash debe ser actualizado
            
        Example:
            if hasher.needs_rehash(user.password_hash):
                user.password_hash = hasher.hash_password(plain_password)
        """
        try:
            # Extraer el número de rounds del hash bcrypt
            # El formato es: $2b$12$salthash
            parts = hashed_password.split('$')
            
            # Validar formato bcrypt
            if len(parts) >= 4 and parts[1] in ('2a', '2b', '2y'):
                # parts[2] contiene los rounds (formato: "12" para 2^12 rounds)
                current_rounds = int(parts[2])
                return current_rounds < self.bcrypt_rounds
        except (ValueError, IndexError):
            # Si no se puede parsear, asumir que necesita rehash
            return True
        
        return False
    
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
