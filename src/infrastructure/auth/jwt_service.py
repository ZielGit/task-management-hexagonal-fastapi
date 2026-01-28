from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError

from ..config.settings import get_settings


settings = get_settings()


class JWTService:
    """
    Servicio para manejo de JSON Web Tokens.
    
    Responsabilidades:
    - Crear tokens de acceso
    - Decodificar y validar tokens
    - Verificar expiración
    """
    
    def __init__(self):
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.expiration_minutes = settings.JWT_EXPIRATION_MINUTES
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un token JWT de acceso.
        
        Args:
            data: Datos a codificar en el token (típicamente user_id, email)
            expires_delta: Tiempo de expiración personalizado (opcional)
            
        Returns:
            Token JWT codificado como string
            
        Example:
            token = jwt_service.create_access_token(
                data={"sub": user_id, "email": user_email}
            )
        """
        # Copiar datos para no mutar el original
        to_encode = data.copy()
        
        # Calcular tiempo de expiración
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.expiration_minutes)
        
        # Agregar claims estándar
        to_encode.update({
            "exp": expire,  # Expiration time
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"  # Token type
        })
        
        # Codificar token
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decodifica y valida un token JWT.
        
        Args:
            token: Token JWT a decodificar
            
        Returns:
            Diccionario con los datos del payload
            
        Raises:
            JWTError: Si el token es inválido
            ExpiredSignatureError: Si el token ha expirado
            
        Example:
            try:
                payload = jwt_service.decode_token(token)
                user_id = payload.get("sub")
            except JWTError:
                # Handle invalid token
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
            
        except ExpiredSignatureError:
            raise ExpiredSignatureError("Token has expired")
        
        except JWTError as e:
            raise JWTError(f"Invalid token: {str(e)}")
    
    def verify_token(self, token: str) -> bool:
        """
        Verifica si un token es válido sin decodificarlo completamente.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            True si el token es válido, False en caso contrario
        """
        try:
            self.decode_token(token)
            return True
        except (JWTError, ExpiredSignatureError):
            return False
    
    def get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        Obtiene la fecha de expiración de un token.
        
        Args:
            token: Token JWT
            
        Returns:
            Datetime de expiración o None si el token es inválido
        """
        try:
            payload = self.decode_token(token)
            exp_timestamp = payload.get("exp")
            
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
            
            return None
            
        except (JWTError, ExpiredSignatureError):
            return None
    
    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crea un refresh token de larga duración.
        
        Args:
            data: Datos a codificar
            expires_delta: Tiempo de expiración (default: 7 días)
            
        Returns:
            Refresh token codificado
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
