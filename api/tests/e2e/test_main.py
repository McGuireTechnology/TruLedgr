import pytest
from httpx import AsyncClient

from api.main import app


@pytest.mark.asyncio
async def test_root_returns_bonjour():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.get("/")
        assert resp.status_code == 200
        assert resp.json().get("message", "").startswith("Bonjour")


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        resp = await client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("status") == "healthy"
        assert "Bonjour" in data.get("message", "")
