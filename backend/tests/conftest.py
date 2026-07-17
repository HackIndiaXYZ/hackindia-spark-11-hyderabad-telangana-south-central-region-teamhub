import os
os.environ["MODEL_PROVIDER"] = "fallback"

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, create_tables, async_session_factory, Base

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
