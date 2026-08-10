import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_request_upload(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "screenshot.png",
        "size": 1024 * 1024 * 2, # 2MB
        "mime_type": "image/png"
    })
    
    assert resp.status_code == 201
    data = resp.json()
    assert "upload_id" in data
    assert "upload_url" in data
    # Because we don't have R2_ACCOUNT_ID set in test env, it uses the mock URL
    assert data["upload_url"].startswith("http://mock.r2/upload/")


@pytest.mark.asyncio
async def test_request_upload_too_large(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "huge.iso",
        "size": 1024 * 1024 * 500, # 500MB (limit is 100MB)
        "mime_type": "application/octet-stream"
    })
    assert resp.status_code == 400
    assert "exceeds maximum allowed" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_complete_upload_and_download_share(auth_client: AsyncClient):
    # Request
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "valid.png",
        "size": 1024,
        "mime_type": "image/png"
    })
    upload_id = resp.json()["upload_id"]
    
    # Complete
    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    assert resp.status_code == 201
    share_data = resp.json()
    assert "token" in share_data
    token = share_data["token"]
    
    # Download Flow
    resp = await auth_client.get(f"/api/v1/shares/{token}/download")
    assert resp.status_code == 200
    dl_data = resp.json()
    assert "download_url" in dl_data
    assert dl_data["download_url"].startswith("http://mock.r2/download/")
    assert dl_data["filename"] == "valid.png"
    
    # Attempt complete again on same upload ID should fail
    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    assert resp.status_code == 400
    assert "is not pending" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_share_download(auth_client: AsyncClient):
    resp = await auth_client.get("/api/v1/shares/invalid-token-123/download")
    assert resp.status_code == 404
