import pytest
from uuid import uuid4
from datetime import datetime

from src.domain.entities.user import User


class TestUserCreation:
    """Tests de creación de User"""
    
    def test_create_user_with_valid_data(self):
        """Debe crear un usuario válido con datos correctos"""
        # Act
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashed_password_123"
        )
        
        # Assert
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password_123"
        assert user.is_active is True
        assert user.is_verified is False
        assert user.id is not None
        assert isinstance(user.created_at, datetime)
    
    def test_create_user_validates_empty_email(self):
        """Debe rechazar emails vacíos"""
        with pytest.raises(ValueError, match="Email cannot be empty"):
            User(
                email="",
                username="testuser",
                hashed_password="hash"
            )
    
    def test_create_user_validates_invalid_email_format(self):
        """Debe rechazar emails con formato inválido"""
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                email="invalid-email",
                username="testuser",
                hashed_password="hash"
            )
        
        with pytest.raises(ValueError, match="Invalid email format"):
            User(
                email="no-at-sign.com",
                username="testuser",
                hashed_password="hash"
            )
    
    def test_create_user_normalizes_email_to_lowercase(self):
        """Debe convertir email a minúsculas"""
        user = User(
            email="Test@EXAMPLE.COM",
            username="testuser",
            hashed_password="hash"
        )
        
        assert user.email == "test@example.com"
    
    def test_create_user_validates_empty_username(self):
        """Debe rechazar usernames vacíos"""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            User(
                email="test@example.com",
                username="",
                hashed_password="hash"
            )
    
    def test_create_user_validates_short_username(self):
        """Debe rechazar usernames menores a 3 caracteres"""
        with pytest.raises(ValueError, match="at least 3 characters"):
            User(
                email="test@example.com",
                username="ab",
                hashed_password="hash"
            )
    
    def test_create_user_validates_username_characters(self):
        """Debe rechazar usernames con caracteres inválidos"""
        with pytest.raises(ValueError, match="can only contain"):
            User(
                email="test@example.com",
                username="user@name",
                hashed_password="hash"
            )
        
        with pytest.raises(ValueError, match="can only contain"):
            User(
                email="test@example.com",
                username="user name",
                hashed_password="hash"
            )
    
    def test_create_user_accepts_valid_username_characters(self):
        """Debe aceptar usernames con letras, números, guiones y guiones bajos"""
        user = User(
            email="test@example.com",
            username="user_name-123",
            hashed_password="hash"
        )
        
        assert user.username == "user_name-123"


class TestUserBehavior:
    """Tests de comportamiento de User"""
    
    def test_change_password(self):
        """Debe cambiar la contraseña del usuario"""
        # Arrange
        user = User("test@example.com", "testuser", "old_hash")
        
        # Act
        user.change_password("new_hash")
        
        # Assert
        assert user.hashed_password == "new_hash"
    
    def test_activate_user(self):
        """Debe activar un usuario desactivado"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_active=False)
        assert not user.is_active
        
        # Act
        user.activate()
        
        # Assert
        assert user.is_active
    
    def test_activate_already_active_user_is_idempotent(self):
        """Activar usuario ya activo debe ser idempotente"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_active=True)
        
        # Act
        user.activate()
        
        # Assert
        assert user.is_active
    
    def test_deactivate_user(self):
        """Debe desactivar un usuario activo"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_active=True)
        
        # Act
        user.deactivate()
        
        # Assert
        assert not user.is_active
    
    def test_deactivate_already_inactive_user_is_idempotent(self):
        """Desactivar usuario ya inactivo debe ser idempotente"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_active=False)
        
        # Act
        user.deactivate()
        
        # Assert
        assert not user.is_active
    
    def test_verify_user(self):
        """Debe verificar un usuario no verificado"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_verified=False)
        
        # Act
        user.verify()
        
        # Assert
        assert user.is_verified
    
    def test_verify_already_verified_user_is_idempotent(self):
        """Verificar usuario ya verificado debe ser idempotente"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_verified=True)
        
        # Act
        user.verify()
        
        # Assert
        assert user.is_verified
    
    def test_record_login(self):
        """Debe registrar el último login"""
        # Arrange
        user = User("test@example.com", "testuser", "hash")
        assert user.last_login is None
        
        # Act
        user.record_login()
        
        # Assert
        assert user.last_login is not None
        assert isinstance(user.last_login, datetime)
    
    def test_record_login_updates_timestamp(self):
        """Cada login debe actualizar el timestamp"""
        # Arrange
        user = User("test@example.com", "testuser", "hash")
        user.record_login()
        first_login = user.last_login
        
        # Act
        import time
        time.sleep(0.01)  # Pequeña espera
        user.record_login()
        
        # Assert
        assert user.last_login > first_login
    
    def test_cannot_login_as_inactive_user(self):
        """No debe permitir login de usuario inactivo"""
        # Arrange
        user = User("test@example.com", "testuser", "hash", is_active=False)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Cannot login as inactive user"):
            user.record_login()


class TestUserQueries:
    """Tests de métodos de consulta"""
    
    def test_can_login_when_active(self):
        """Usuario activo puede hacer login"""
        user = User("test@example.com", "testuser", "hash", is_active=True)
        assert user.can_login()
    
    def test_cannot_login_when_inactive(self):
        """Usuario inactivo no puede hacer login"""
        user = User("test@example.com", "testuser", "hash", is_active=False)
        assert not user.can_login()
    
    def test_needs_verification_when_not_verified(self):
        """Usuario no verificado necesita verificación"""
        user = User("test@example.com", "testuser", "hash", is_verified=False)
        assert user.needs_verification()
    
    def test_does_not_need_verification_when_verified(self):
        """Usuario verificado no necesita verificación"""
        user = User("test@example.com", "testuser", "hash", is_verified=True)
        assert not user.needs_verification()
    
    def test_has_logged_in_when_last_login_exists(self):
        """Debe detectar si ha iniciado sesión alguna vez"""
        user = User("test@example.com", "testuser", "hash")
        assert not user.has_logged_in()
        
        user.record_login()
        assert user.has_logged_in()


class TestUserEquality:
    """Tests de igualdad entre usuarios"""
    
    def test_users_with_same_id_are_equal(self):
        """Usuarios con el mismo ID son iguales"""
        user_id = uuid4()
        user1 = User("test1@example.com", "user1", "hash1", user_id=user_id)
        user2 = User("test2@example.com", "user2", "hash2", user_id=user_id)
        
        assert user1 == user2
    
    def test_users_with_different_ids_are_not_equal(self):
        """Usuarios con diferentes IDs no son iguales"""
        user1 = User("test@example.com", "user1", "hash")
        user2 = User("test@example.com", "user2", "hash")
        
        assert user1 != user2
    
    def test_user_can_be_used_in_set(self):
        """Usuarios pueden usarse en sets"""
        user1 = User("test1@example.com", "user1", "hash")
        user2 = User("test2@example.com", "user2", "hash")
        
        user_set = {user1, user2}
        
        assert len(user_set) == 2
        assert user1 in user_set


class TestUserValidation:
    """Tests de validación de datos"""
    
    def test_email_max_length(self):
        """Email no debe exceder 255 caracteres"""
        long_email = "a" * 250 + "@test.com"
        
        with pytest.raises(ValueError, match="cannot exceed 255"):
            User(long_email, "user", "hash")
    
    def test_username_max_length(self):
        """Username no debe exceder 50 caracteres"""
        long_username = "a" * 51
        
        with pytest.raises(ValueError, match="cannot exceed 50"):
            User("test@example.com", long_username, "hash")
    
    def test_strips_whitespace_from_email(self):
        """Debe eliminar espacios del email"""
        user = User("  test@example.com  ", "user", "hash")
        assert user.email == "test@example.com"
    
    def test_strips_whitespace_from_username(self):
        """Debe eliminar espacios del username"""
        user = User("test@example.com", "  username  ", "hash")
        assert user.username == "username"
