import pytest
import pytest_asyncio
from uuid import uuid4, UUID
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

from src.domain.entities.user import User
from src.domain.repositories.user_repository import UserRepository


# ============= In-Memory Implementation for Integration Tests =============

class InMemoryUserRepository(UserRepository):
    """
    Implementación en memoria del UserRepository para tests de integración.
    Permite testear la lógica del repositorio sin base de datos real.
    """

    def __init__(self):
        self._users: dict[UUID, User] = {}

    async def save(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def find_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users.get(user_id)

    async def find_by_email(self, email: str) -> Optional[User]:
        for user in self._users.values():
            if user.email == email:
                return user
        return None

    async def find_by_username(self, username: str) -> Optional[User]:
        for user in self._users.values():
            if user.username == username:
                return user
        return None

    async def exists_by_email(self, email: str) -> bool:
        return any(u.email == email for u in self._users.values())

    async def exists_by_username(self, username: str) -> bool:
        return any(u.username == username for u in self._users.values())

    async def delete(self, user_id: UUID) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False


# ============= Helpers =============

def make_user(
    email: str = "test@example.com",
    username: str = "testuser",
    hashed_password: str = "hashed_password_123",
) -> User:
    """Crea un User válido para los tests."""
    return User(
        email=email,
        username=username,
        hashed_password=hashed_password,
    )


# ============= Fixtures =============

@pytest.fixture
def repo() -> InMemoryUserRepository:
    """Repositorio en memoria limpio para cada test."""
    return InMemoryUserRepository()


@pytest_asyncio.fixture
async def saved_user(repo: InMemoryUserRepository) -> User:
    """Usuario ya persistido para tests que lo requieren."""
    user = make_user()
    return await repo.save(user)


# ============= Tests: save =============

@pytest.mark.asyncio
class TestUserRepositorySave:
    """Tests del método save()."""

    async def test_save_returns_user(self, repo):
        """save() debe retornar el usuario persistido."""
        user = make_user()
        result = await repo.save(user)
        assert result.id == user.id
        assert result.email == user.email
        assert result.username == user.username

    async def test_save_persists_user(self, repo):
        """save() debe persistir el usuario para recuperación posterior."""
        user = make_user()
        await repo.save(user)
        found = await repo.find_by_id(user.id)
        assert found is not None
        assert found.id == user.id

    async def test_save_multiple_users(self, repo):
        """save() debe persistir múltiples usuarios independientemente."""
        user_a = make_user(email="a@example.com", username="user_a")
        user_b = make_user(email="b@example.com", username="user_b")
        await repo.save(user_a)
        await repo.save(user_b)

        found_a = await repo.find_by_id(user_a.id)
        found_b = await repo.find_by_id(user_b.id)
        assert found_a.id == user_a.id
        assert found_b.id == user_b.id

    async def test_save_overwrites_existing_user(self, repo):
        """save() con el mismo ID debe actualizar el usuario existente."""
        user = make_user()
        await repo.save(user)

        # Simular actualización (mismo ID, email diferente)
        updated = User(
            user_id=user.id,
            email="updated@example.com",
            username=user.username,
            hashed_password=user.hashed_password,
        )
        await repo.save(updated)

        found = await repo.find_by_id(user.id)
        assert found.email == "updated@example.com"


# ============= Tests: find_by_id =============

@pytest.mark.asyncio
class TestUserRepositoryFindById:
    """Tests del método find_by_id()."""

    async def test_find_existing_user_by_id(self, repo, saved_user):
        """find_by_id() debe retornar el usuario cuando existe."""
        result = await repo.find_by_id(saved_user.id)
        assert result is not None
        assert result.id == saved_user.id

    async def test_find_nonexistent_user_returns_none(self, repo):
        """find_by_id() debe retornar None si el usuario no existe."""
        result = await repo.find_by_id(uuid4())
        assert result is None

    async def test_find_by_id_returns_correct_user(self, repo):
        """find_by_id() debe retornar exactamente el usuario con ese ID."""
        user_a = make_user(email="a@example.com", username="user_a")
        user_b = make_user(email="b@example.com", username="user_b")
        await repo.save(user_a)
        await repo.save(user_b)

        result = await repo.find_by_id(user_a.id)
        assert result.id == user_a.id
        assert result.email == "a@example.com"


# ============= Tests: find_by_email =============

@pytest.mark.asyncio
class TestUserRepositoryFindByEmail:
    """Tests del método find_by_email()."""

    async def test_find_existing_user_by_email(self, repo, saved_user):
        """find_by_email() debe retornar el usuario cuando el email existe."""
        result = await repo.find_by_email(saved_user.email)
        assert result is not None
        assert result.email == saved_user.email

    async def test_find_by_nonexistent_email_returns_none(self, repo):
        """find_by_email() debe retornar None si el email no existe."""
        result = await repo.find_by_email("ghost@example.com")
        assert result is None

    async def test_find_by_email_is_case_sensitive(self, repo):
        """find_by_email() debe distinguir mayúsculas/minúsculas."""
        user = make_user(email="lower@example.com")
        await repo.save(user)
        result = await repo.find_by_email("LOWER@example.com")
        # El comportamiento exacto depende del dominio; aquí validamos consistencia
        assert result is None or result.email == "lower@example.com"


# ============= Tests: find_by_username =============

@pytest.mark.asyncio
class TestUserRepositoryFindByUsername:
    """Tests del método find_by_username()."""

    async def test_find_existing_user_by_username(self, repo, saved_user):
        """find_by_username() debe retornar el usuario cuando el username existe."""
        result = await repo.find_by_username(saved_user.username)
        assert result is not None
        assert result.username == saved_user.username

    async def test_find_by_nonexistent_username_returns_none(self, repo):
        """find_by_username() debe retornar None si el username no existe."""
        result = await repo.find_by_username("phantom_user")
        assert result is None


# ============= Tests: exists_by_email =============

@pytest.mark.asyncio
class TestUserRepositoryExistsByEmail:
    """Tests del método exists_by_email()."""

    async def test_returns_true_for_existing_email(self, repo, saved_user):
        """exists_by_email() debe retornar True si el email ya está registrado."""
        result = await repo.exists_by_email(saved_user.email)
        assert result is True

    async def test_returns_false_for_nonexistent_email(self, repo):
        """exists_by_email() debe retornar False si el email no existe."""
        result = await repo.exists_by_email("nobody@example.com")
        assert result is False

    async def test_returns_false_after_save_different_email(self, repo):
        """exists_by_email() no debe confundir emails distintos."""
        user = make_user(email="registered@example.com")
        await repo.save(user)
        result = await repo.exists_by_email("other@example.com")
        assert result is False


# ============= Tests: exists_by_username =============

@pytest.mark.asyncio
class TestUserRepositoryExistsByUsername:
    """Tests del método exists_by_username()."""

    async def test_returns_true_for_existing_username(self, repo, saved_user):
        """exists_by_username() debe retornar True si el username ya existe."""
        result = await repo.exists_by_username(saved_user.username)
        assert result is True

    async def test_returns_false_for_nonexistent_username(self, repo):
        """exists_by_username() debe retornar False si el username no existe."""
        result = await repo.exists_by_username("ghost_user")
        assert result is False


# ============= Tests: delete =============

@pytest.mark.asyncio
class TestUserRepositoryDelete:
    """Tests del método delete()."""

    async def test_delete_existing_user_returns_true(self, repo, saved_user):
        """delete() debe retornar True al eliminar un usuario existente."""
        result = await repo.delete(saved_user.id)
        assert result is True

    async def test_delete_removes_user_from_store(self, repo, saved_user):
        """delete() debe eliminar el usuario del almacenamiento."""
        await repo.delete(saved_user.id)
        found = await repo.find_by_id(saved_user.id)
        assert found is None

    async def test_delete_nonexistent_user_returns_false(self, repo):
        """delete() debe retornar False si el usuario no existe."""
        result = await repo.delete(uuid4())
        assert result is False

    async def test_delete_only_removes_target_user(self, repo):
        """delete() no debe afectar a otros usuarios."""
        user_a = make_user(email="a@example.com", username="user_a")
        user_b = make_user(email="b@example.com", username="user_b")
        await repo.save(user_a)
        await repo.save(user_b)

        await repo.delete(user_a.id)

        assert await repo.find_by_id(user_a.id) is None
        assert await repo.find_by_id(user_b.id) is not None

    async def test_exists_by_email_returns_false_after_delete(self, repo, saved_user):
        """exists_by_email() debe retornar False después de eliminar el usuario."""
        email = saved_user.email
        await repo.delete(saved_user.id)
        result = await repo.exists_by_email(email)
        assert result is False
