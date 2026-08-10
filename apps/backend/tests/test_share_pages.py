import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_share_page_image(auth_client: AsyncClient):
    """Full upload flow then rendering the HTML share page."""
    # Request upload
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "photo.png",
        "size": 512 * 1024,
        "mime_type": "image/png",
    })
    assert resp.status_code == 201
    upload_id = resp.json()["upload_id"]

    # Complete upload
    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    assert resp.status_code == 201
    token = resp.json()["token"]

    # GET the HTML share page
    resp = await auth_client.get(f"/s/{token}")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    body = resp.text

    # Verify Open Graph tags
    assert 'property="og:title"' in body
    assert 'property="og:image"' in body
    assert "photo.png" in body
    assert "Snaply" in body
    assert "Download" in body

    # Verify no internal IDs are exposed
    assert upload_id not in body
    assert "storage_key" not in body
    assert "password_hash" not in body


@pytest.mark.asyncio
async def test_share_page_video(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "clip.mp4",
        "size": 1024 * 1024 * 5,
        "mime_type": "video/mp4",
    })
    upload_id = resp.json()["upload_id"]

    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    token = resp.json()["token"]

    resp = await auth_client.get(f"/s/{token}")
    assert resp.status_code == 200
    body = resp.text
    assert "<video" in body
    assert "clip.mp4" in body


@pytest.mark.asyncio
async def test_share_page_generic_file(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "archive.zip",
        "size": 1024 * 1024,
        "mime_type": "application/zip",
    })
    upload_id = resp.json()["upload_id"]

    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    token = resp.json()["token"]

    resp = await auth_client.get(f"/s/{token}")
    assert resp.status_code == 200
    body = resp.text
    assert "archive.zip" in body
    assert "application/zip" in body
    assert "Download" in body


@pytest.mark.asyncio
async def test_share_page_invalid_token(auth_client: AsyncClient):
    resp = await auth_client.get("/s/nonexistent-token-abc123")
    assert resp.status_code == 404
    body = resp.text
    assert "text/html" in resp.headers["content-type"]
    assert "Not Found" in body


@pytest.mark.asyncio
async def test_share_page_revoked_link(auth_client: AsyncClient):
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "to_revoke.png",
        "size": 1024,
        "mime_type": "image/png",
    })
    upload_id = resp.json()["upload_id"]

    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    share_id = resp.json()["id"]
    token = resp.json()["token"]

    # Revoke the share link
    resp = await auth_client.delete(f"/api/v1/shares/{share_id}")
    assert resp.status_code == 204

    # Now accessing the page should give a 404
    resp = await auth_client.get(f"/s/{token}")
    assert resp.status_code == 404
    assert "Not Found" in resp.text


@pytest.mark.asyncio
async def test_share_page_security_no_credentials(auth_client: AsyncClient):
    """Verify no R2 credentials or internal keys leak into the HTML."""
    resp = await auth_client.post("/api/v1/uploads/request", json={
        "filename": "secret.png",
        "size": 1024,
        "mime_type": "image/png",
    })
    upload_id = resp.json()["upload_id"]
    resp = await auth_client.post(f"/api/v1/uploads/{upload_id}/complete")
    token = resp.json()["token"]

    resp = await auth_client.get(f"/s/{token}")
    body = resp.text

    # No R2 secrets or raw credentials must appear
    assert "R2_ACCESS_KEY" not in body
    assert "R2_SECRET" not in body
    assert "SECRET_KEY" not in body
    # Internal DB IDs must not appear as standalone plain text (they would only
    # appear inside a pre-signed URL, which is the intended behavior)
    assert "storage_key" not in body
    assert "password_hash" not in body
