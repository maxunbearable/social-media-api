import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.sql import select
from api.database import database, post_table, comment_table, user_table

os.environ["ENV_STATE"] = "test"

from api.main import app


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture()
def client() -> Generator:
    yield TestClient(app)


@pytest.fixture(autouse=True)
async def db() -> AsyncGenerator:
    await database.connect()
    yield
    await database.disconnect()


@pytest.fixture(autouse=True)
async def clean_db() -> AsyncGenerator:
    await database.execute(comment_table.delete())
    await database.execute(post_table.delete())
    yield


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac

@pytest.fixture()
async def register_user(async_client) -> dict:
    user_details = { "email": "test@test.com", "password": "test" }
    await async_client.post("/register", json=user_details)
    query = select(user_table).where(user_table.c.email == user_details["email"])
    result = await database.fetch_one(query)
    user_details["id"] = result["id"]
    return user_details