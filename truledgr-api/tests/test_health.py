from httpx import AsyncClient
from truledgr_api.main import app


async def test_ping():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/health/ping")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
