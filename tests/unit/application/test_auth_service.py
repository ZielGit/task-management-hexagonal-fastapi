import pytest
from uuid import uuid4

from src.infrastructure.auth.auth_service_impl import AuthServiceImpl


class TestAuthServicePasswordHashing:
    """Tests de hashing de contraseñas"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthServiceImpl()
    
    def test_hash_password_returns_different_hash(self, auth_service):
        """Debe generar hash diferente al texto plano"""
        password = "MySecurePassword123!"
        hashed = auth_service.hash_password(password)
        
        assert hashed != password
        assert len(hashed) > len(password)
    
    def test_hash_same_password_twice_gives_different_hashes(self, auth_service):
        """Dos hashes de la misma contraseña deben ser diferentes (salt)"""
        password = "MySecurePassword123!"
        hash1 = auth_service.hash_password(password)
        hash2 = auth_service.hash_password(password)
        
        # Aunque son de la misma password, el salt hace que sean diferentes
        assert hash1 != hash2
    
    def test_verify_correct_password(self, auth_service):
        """Debe verificar correctamente una contraseña válida"""
        password = "MySecurePassword123!"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(password, hashed) is True
    
    def test_verify_incorrect_password(self, auth_service):
        """Debe rechazar contraseña incorrecta"""
        password = "MySecurePassword123!"
        wrong_password = "WrongPassword456!"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password(wrong_password, hashed) is False
    
    def test_verify_password_is_case_sensitive(self, auth_service):
        """Verificación debe ser case-sensitive"""
        password = "MyPassword123!"
        hashed = auth_service.hash_password(password)
        
        assert auth_service.verify_password("mypassword123!", hashed) is False
        assert auth_service.verify_password("MYPASSWORD123!", hashed) is False


class TestAuthServiceTokenGeneration:
    """Tests de generación de tokens JWT"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthServiceImpl()
    
    @pytest.fixture
    def user_id(self):
        return uuid4()
    
    @pytest.fixture
    def email(self):
        return "test@example.com"
    
    def test_create_access_token(self, auth_service, user_id, email):
        """Debe crear un token JWT válido"""
        token = auth_service.create_access_token(user_id, email)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        # JWT tiene formato: header.payload.signature
        assert token.count('.') == 2
    
    def test_different_users_get_different_tokens(self, auth_service):
        """Usuarios diferentes deben tener tokens diferentes"""
        user1_id = uuid4()
        user2_id = uuid4()
        
        token1 = auth_service.create_access_token(user1_id, "user1@example.com")
        token2 = auth_service.create_access_token(user2_id, "user2@example.com")
        
        assert token1 != token2
    
    def test_decode_valid_token(self, auth_service, user_id, email):
        """Debe decodificar correctamente un token válido"""
        token = auth_service.create_access_token(user_id, email)
        payload = auth_service.decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert "exp" in payload  # Expiration time
        assert "iat" in payload  # Issued at
    
    def test_decode_invalid_token_raises_error(self, auth_service):
        """Debe rechazar token inválido"""
        invalid_token = "invalid.token.here"
        
        with pytest.raises(Exception):
            auth_service.decode_token(invalid_token)
    
    def test_decode_malformed_token_raises_error(self, auth_service):
        """Debe rechazar token malformado"""
        malformed_token = "not-a-valid-jwt"
        
        with pytest.raises(Exception):
            auth_service.decode_token(malformed_token)


class TestAuthServicePasswordValidation:
    """Tests de validación de fortaleza de contraseñas"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthServiceImpl()
    
    def test_validate_strong_password(self, auth_service):
        """Debe aceptar contraseña fuerte"""
        password = "MySecure@Pass123"
        is_valid, message = auth_service.validate_password_strength(password)
        
        assert is_valid is True
        assert "strong" in message.lower()
    
    def test_reject_short_password(self, auth_service):
        """Debe rechazar contraseña muy corta"""
        password = "Short1!"
        is_valid, message = auth_service.validate_password_strength(password)
        
        assert is_valid is False
        assert "8 characters" in message
    
    def test_reject_password_without_uppercase(self, auth_service):
        """Debe rechazar contraseña sin mayúsculas"""
        password = "mypassword123!"
        is_valid, message = auth_service.validate_password_strength(password)
        
        assert is_valid is False
        assert "uppercase" in message.lower()
    
    def test_reject_password_without_lowercase(self, auth_service):
        """Debe rechazar contraseña sin minúsculas"""
        password = "MYPASSWORD123!"
        is_valid, message = auth_service.validate_password_strength(password)
        
        assert is_valid is False
        assert "lowercase" in message.lower()
    
    def test_reject_password_without_number(self, auth_service):
        """Debe rechazar contraseña sin números"""
        password = "MyPassword!"
        is_valid, message = auth_service.validate_password_strength(password)
        
        assert is_valid is False
        assert "number" in message.lower()
    
    def test_reject_password_without_special_char(self, auth_service):
        """Debe rechazar contraseña sin caracteres especiales"""
        password = "MyPassword123"
        is_valid, message = auth_service.validate_password_strength(password)
        
        assert is_valid is False
        assert "special character" in message.lower()
    
    @pytest.mark.parametrize("password", [
        "MySecure@Pass123",
        "Another!Strong1Pass",
        "Complex#Password2024",
        "Valid_Pass123!",
    ])
    def test_accept_various_strong_passwords(self, auth_service, password):
        """Debe aceptar varias contraseñas fuertes"""
        is_valid, _ = auth_service.validate_password_strength(password)
        assert is_valid is True


class TestAuthServiceIntegration:
    """Tests de integración del AuthService"""
    
    @pytest.fixture
    def auth_service(self):
        return AuthServiceImpl()
    
    def test_full_authentication_flow(self, auth_service):
        """Test del flujo completo de autenticación"""
        # 1. Validar contraseña
        password = "MySecurePass123!"
        is_valid, _ = auth_service.validate_password_strength(password)
        assert is_valid
        
        # 2. Hashear contraseña
        hashed = auth_service.hash_password(password)
        assert hashed != password
        
        # 3. Verificar contraseña
        assert auth_service.verify_password(password, hashed)
        
        # 4. Crear token
        user_id = uuid4()
        email = "test@example.com"
        token = auth_service.create_access_token(user_id, email)
        assert token is not None
        
        # 5. Decodificar token
        payload = auth_service.decode_token(token)
        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
    
    def test_authentication_rejects_wrong_password(self, auth_service):
        """Flujo de autenticación debe rechazar contraseña incorrecta"""
        # Arrange
        correct_password = "CorrectPass123!"
        wrong_password = "WrongPass456!"
        
        hashed = auth_service.hash_password(correct_password)
        
        # Act & Assert
        assert auth_service.verify_password(wrong_password, hashed) is False
