import os
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from fastapi import Request, Response
import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from sqlalchemy.sql import select
from api.database import database, post_table, comment_table, user_table, like_table

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
    await database.execute(comment_table.delete())
    await database.execute(like_table.delete())
    await database.execute(post_table.delete())
    await database.execute(user_table.delete())
    yield
    await database.disconnect()


@pytest.fixture()
async def async_client(client) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url=client.base_url) as ac:
        yield ac

@pytest.fixture()
async def registered_user(async_client) -> dict:
    user_details = { "email": "test@test.com", "password": "test" }
    await async_client.post("/register", json=user_details)
    query = select(user_table).where(user_table.c.email == user_details["email"])
    result = await database.fetch_one(query)
    user_details["id"] = result["id"]
    return user_details

@pytest.fixture()
async def confirmed_user(registered_user) -> dict:
    query = user_table.update().where(user_table.c.email == registered_user["email"]).values(confirmed=True)
    await database.execute(query)
    return registered_user

@pytest.fixture()
async def logged_in_token(async_client, confirmed_user: dict) -> str:
    response = await async_client.post("/token", data={"username": confirmed_user["email"], "password": confirmed_user["password"]})
    return response.json()["access_token"]

@pytest.fixture(autouse=True)
async def mock_httpx_client(mocker):
    mocked_client = mocker.patch("api.tasks.httpx.AsyncClient")
    mocked_async_client = Mock()
    response = Response(status_code=200, content="")
    response.raise_for_status = Mock()
    response.content = b"Mock response content"
    mocked_async_client.post = AsyncMock(return_value=response)
    mocked_client.return_value.__aenter__.return_value = mocked_async_client
    
    return mocked_async_client