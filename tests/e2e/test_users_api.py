import pytest
import pytest_asyncio
from uuid import uuid4

from src.main import app


# ============= Helpers =============

def unique_user():
    """Genera credenciales únicas para evitar conflictos entre tests."""
    uid = uuid4().hex[:8]
    return {
        "email": f"user_{uid}@example.com",
        "username": f"user_{uid}",
        "password": "SecurePass1!"
    }


async def register_and_login(client):
    """
    Registra un usuario único y hace login.
    Retorna (register_data, token).
    """
    payload = unique_user()

    reg = await client.post("/api/auth/register", json=payload)
    assert reg.status_code == 201, f"Register falló: {reg.json()}"

    login = await client.post(
        "/api/auth/login",
        json={"email": payload["email"], "password": payload["password"]}
    )
    assert login.status_code == 200, f"Login falló: {login.json()}"

    return reg.json(), login.json()["access_token"], payload


# ============= Fixtures =============

@pytest.fixture
def auth_headers():
    """Headers con token JWT mock para endpoints protegidos."""
    return {"Authorization": "Bearer fake-jwt-token-for-testing"}


# ============= Tests: POST /api/auth/register =============

@pytest.mark.asyncio
class TestRegisterEndpoint:
    """Tests del endpoint POST /api/auth/register."""

    async def test_register_success(self, client):
        """Debe registrar un usuario con datos válidos."""
        payload = unique_user()
        response = await client.post("/api/auth/register", json=payload)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert "id" in data
        assert "password" not in data
        assert "password_hash" not in data

    async def test_register_returns_correct_schema(self, client):
        """La respuesta debe cumplir el schema UserResponseDTO."""
        response = await client.post("/api/auth/register", json=unique_user())

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "email" in data
        assert "username" in data

    async def test_register_duplicate_email_returns_400(self, client):
        """Debe retornar 400 si el email ya está registrado."""
        payload = unique_user()
        await client.post("/api/auth/register", json=payload)

        # Mismo email, distinto username
        duplicate = {**payload, "username": f"other_{uuid4().hex[:6]}"}
        response = await client.post("/api/auth/register", json=duplicate)

        assert response.status_code == 400
        assert "detail" in response.json()

    async def test_register_duplicate_username_returns_400(self, client):
        """Debe retornar 400 si el username ya está registrado."""
        payload = unique_user()
        await client.post("/api/auth/register", json=payload)

        # Mismo username, distinto email
        duplicate = {**payload, "email": f"other_{uuid4().hex[:6]}@example.com"}
        response = await client.post("/api/auth/register", json=duplicate)

        assert response.status_code == 400

    async def test_register_invalid_email_returns_422(self, client):
        """Debe retornar 422 si el email tiene formato inválido."""
        payload = {**unique_user(), "email": "not-an-email"}
        response = await client.post("/api/auth/register", json=payload)

        assert response.status_code == 422

    async def test_register_weak_password_returns_422(self, client):
        """Debe retornar 422 si la contraseña no cumple los requisitos."""
        payload = {**unique_user(), "password": "1234"}
        response = await client.post("/api/auth/register", json=payload)

        assert response.status_code == 422

    async def test_register_empty_username_returns_422(self, client):
        """Debe retornar 422 si el username está vacío."""
        payload = {**unique_user(), "username": ""}
        response = await client.post("/api/auth/register", json=payload)

        assert response.status_code == 422

    async def test_register_missing_fields_returns_422(self, client):
        """Debe retornar 422 si faltan campos requeridos."""
        response = await client.post(
            "/api/auth/register",
            json={"email": "only@example.com"}
        )

        assert response.status_code == 422


# ============= Tests: POST /api/auth/login =============

@pytest.mark.asyncio
class TestLoginEndpoint:
    """Tests del endpoint POST /api/auth/login."""

    async def test_login_success(self, client):
        """Debe autenticar un usuario con credenciales válidas."""
        _, token, _ = await register_and_login(client)

        assert token is not None
        assert len(token) > 0

    async def test_login_returns_jwt_token(self, client):
        """El token retornado debe ser un JWT válido (3 partes separadas por '.')."""
        payload = unique_user()
        await client.post("/api/auth/register", json=payload)

        response = await client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": payload["password"]}
        )

        assert response.status_code == 200
        token = response.json()["access_token"]
        assert len(token.split(".")) == 3, "JWT debe tener header.payload.signature"

    async def test_login_returns_correct_schema(self, client):
        """La respuesta debe incluir access_token, token_type y expires_in."""
        payload = unique_user()
        await client.post("/api/auth/register", json=payload)

        response = await client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": payload["password"]}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    async def test_login_wrong_password_returns_401(self, client):
        """Debe retornar 401 con contraseña incorrecta."""
        payload = unique_user()
        await client.post("/api/auth/register", json=payload)

        response = await client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": "WrongPassword99!"}
        )

        assert response.status_code == 401
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    async def test_login_nonexistent_email_returns_401(self, client):
        """Debe retornar 401 si el email no está registrado."""
        response = await client.post(
            "/api/auth/login",
            json={"email": f"ghost_{uuid4().hex[:6]}@example.com", "password": "AnyPass1!"}
        )

        assert response.status_code == 401

    async def test_login_missing_credentials_returns_422(self, client):
        """Debe retornar 422 si faltan campos."""
        response = await client.post(
            "/api/auth/login",
            json={"email": "only@example.com"}
        )

        assert response.status_code == 422

    async def test_login_invalid_email_format_returns_422(self, client):
        """Debe retornar 422 si el email tiene formato inválido."""
        response = await client.post(
            "/api/auth/login",
            json={"email": "not-valid", "password": "SecurePass1!"}
        )

        assert response.status_code == 422


# ============= Tests: GET /api/auth/me =============

@pytest.mark.asyncio
class TestGetCurrentUserEndpoint:
    """Tests del endpoint GET /api/auth/me."""

    async def test_get_me_with_valid_token(self, client):
        """Debe retornar el usuario autenticado con un token válido."""
        user_data, token, payload = await register_and_login(client)

        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == payload["email"]
        assert data["username"] == payload["username"]
        assert "id" in data

    async def test_get_me_without_token_returns_401(self, client):
        """Debe retornar 401 si no se provee token."""
        response = await client.get("/api/auth/me")

        assert response.status_code == 401

    async def test_get_me_with_invalid_token_returns_401(self, client):
        """Debe retornar 401 con un token inválido."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer this.is.invalid"}
        )

        assert response.status_code == 401

    async def test_get_me_with_malformed_header_returns_401(self, client):
        """Debe retornar 401 si el header no tiene el formato 'Bearer <token>'."""
        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": "NotBearer token123"}
        )

        assert response.status_code == 401

    async def test_get_me_does_not_expose_password(self, client):
        """El endpoint /me nunca debe exponer datos sensibles."""
        _, token, _ = await register_and_login(client)

        response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        data = response.json()
        assert "password" not in data
        assert "password_hash" not in data
        assert "hashed_password" not in data


# ============= Tests: POST /api/auth/refresh =============

@pytest.mark.asyncio
class TestRefreshTokenEndpoint:
    """Tests del endpoint POST /api/auth/refresh."""

    async def test_refresh_returns_new_token(self, client):
        """Debe retornar un token nuevo dado un token válido."""
        _, original_token, _ = await register_and_login(client)

        response = await client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {original_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    async def test_refresh_without_token_returns_403(self, client):
        """Debe retornar 401/403 si no se provee token."""
        response = await client.post("/api/auth/refresh")

        assert response.status_code in (401, 403)

    async def test_refresh_with_invalid_token_returns_401(self, client):
        """Debe retornar 401 con un token inválido."""
        response = await client.post(
            "/api/auth/refresh",
            headers={"Authorization": "Bearer invalid.token.here"}
        )

        assert response.status_code == 401


# ============= Tests: flujo completo (happy path) =============

@pytest.mark.asyncio
class TestAuthFullFlow:
    """Tests del flujo completo de autenticación (e2e real)."""

    async def test_register_login_and_get_profile(self, client):
        """Flujo: registrar → login → obtener perfil."""
        payload = unique_user()

        # 1. Registrar
        register_response = await client.post("/api/auth/register", json=payload)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # 2. Login
        login_response = await client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": payload["password"]}
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # 3. Obtener perfil
        me_response = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert me_response.status_code == 200
        profile = me_response.json()
        assert profile["id"] == user_id
        assert profile["email"] == payload["email"]
        assert profile["username"] == payload["username"]

    async def test_register_login_refresh_and_get_profile(self, client):
        """Flujo extendido: registrar → login → refresh → obtener perfil con token nuevo."""
        payload = unique_user()

        # 1. Registrar
        reg = await client.post("/api/auth/register", json=payload)
        assert reg.status_code == 201

        # 2. Login
        login = await client.post(
            "/api/auth/login",
            json={"email": payload["email"], "password": payload["password"]}
        )
        assert login.status_code == 200
        original_token = login.json()["access_token"]

        # 3. Refresh
        refresh = await client.post(
            "/api/auth/refresh",
            headers={"Authorization": f"Bearer {original_token}"}
        )
        assert refresh.status_code == 200
        new_token = refresh.json()["access_token"]

        # 4. /me con token nuevo
        me = await client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {new_token}"}
        )
        assert me.status_code == 200
        assert me.json()["email"] == payload["email"]
