import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "newuser@snaply.dev",
        "password": "testpassword123",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "dupe@snaply.dev",
        "password": "testpassword123",
    })
    resp = await client.post("/api/v1/auth/register", json={
        "email": "dupe@snaply.dev",
        "password": "testpassword123",
    })
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_short_password(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "short@snaply.dev",
        "password": "short",
    })
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "login@snaply.dev",
        "password": "testpassword123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "login@snaply.dev",
        "password": "testpassword123",
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "wrongpw@snaply.dev",
        "password": "testpassword123",
    })
    resp = await client.post("/api/v1/auth/login", json={
        "email": "wrongpw@snaply.dev",
        "password": "wrongpassword",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    resp = await client.post("/api/v1/auth/login", json={
        "email": "ghost@snaply.dev",
        "password": "testpassword123",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "refresh@snaply.dev",
        "password": "testpassword123",
    })
    token = resp.json()["access_token"]
    resp = await client.post("/api/v1/auth/refresh", json={"token": token})
    assert resp.status_code == 200
    assert resp.json()["access_token"] != token


@pytest.mark.asyncio
async def test_logout(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/auth/logout")
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_get_profile(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/me")
    assert resp.status_code == 200
    data = resp.json()
    assert "user" in data
    assert data["user"]["email"] == "test@snaply.dev"
    assert "storage_used" in data
    assert "monthly_uploads" in data


@pytest.mark.asyncio
async def test_unauthorized_profile(client: AsyncClient):
    resp = await client.get("/api/v1/me")
    assert resp.status_code == 403  # No auth header


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "changepw@snaply.dev",
        "password": "oldpassword123",
    })
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    resp = await client.post("/api/v1/auth/password", json={
        "current_password": "oldpassword123",
        "new_password": "newpassword456",
    })
    assert resp.status_code == 204

    # Old password should no longer work
    resp = await client.post("/api/v1/auth/login", json={
        "email": "changepw@snaply.dev",
        "password": "oldpassword123",
    })
    assert resp.status_code == 401

    # New password should work
    resp = await client.post("/api/v1/auth/login", json={
        "email": "changepw@snaply.dev",
        "password": "newpassword456",
    })
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_delete_account(client: AsyncClient):
    resp = await client.post("/api/v1/auth/register", json={
        "email": "deleteme@snaply.dev",
        "password": "testpassword123",
    })
    token = resp.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"

    resp = await client.delete("/api/v1/auth/account")
    assert resp.status_code == 204

    # Logging in should fail
    resp = await client.post("/api/v1/auth/login", json={
        "email": "deleteme@snaply.dev",
        "password": "testpassword123",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_health_ready(client: AsyncClient):
    resp = await client.get("/health/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_uploads_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/uploads")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_upload_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/uploads/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_share_not_found(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/shares/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_usage_empty(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/usage")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_security_headers(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
