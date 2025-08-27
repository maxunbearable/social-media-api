import pytest
from httpx import AsyncClient

from api import security


async def create_post(body: str, async_client: AsyncClient, logged_in_token: str) -> dict:
    response = await async_client.post(
        "/post",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": body},
    )
    return response.json()


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post("Test Post", async_client, logged_in_token)

@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict, logged_in_token: str):
    return await create_comment("Test Comment", async_client, created_post, logged_in_token)

async def create_comment(async_client: AsyncClient, created_post: dict, logged_in_token: str):
    response = await async_client.post(
        "/comment",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": "Test Comment", "post_id": created_post["id"]},
    )
    return response.json()


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient, logged_in_token: str):
    body = "Test Post"
    response = await async_client.post(
        "/post",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": body},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == body
    assert "id" in data
    assert isinstance(data["id"], int)

@pytest.mark.anyio
async def test_create_post_expired_token(async_client: AsyncClient, registered_user: dict, mocker):
    mocker.patch("api.security.access_token_expires_minutes", return_value=-1)
    logged_in_token = security.create_access_token(registered_user["email"])
    response = await async_client.post(
        "/post",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": "Test Post"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Token has expired"

@pytest.mark.anyio
async def test_create_post_missing_data(async_client: AsyncClient, logged_in_token: str):
    response = await async_client.post(
        "/post",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={},
    )
    assert response.status_code == 422


@pytest.mark.anyio
async def test_get_all_posts(async_client: AsyncClient, created_post: dict):
    response = await async_client.get("/posts")
    assert response.status_code == 200
    posts = response.json()
    assert isinstance(posts, list)
    assert len(posts) == 1
    assert posts[0]["body"] == created_post["body"]
    assert posts[0]["id"] == created_post["id"]


@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    logged_in_token: str,
):
    body = "Test Comment"

    response = await async_client.post(
        "/comment",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": body, "post_id": created_post["id"]},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == body
    assert data["post_id"] == created_post["id"]
    assert "id" in data
    assert isinstance(data["id"], int)


@pytest.mark.anyio
async def test_get_comments_on_post(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert isinstance(comments, list)
    assert len(comments) == 1
    assert comments[0]["body"] == created_comment["body"]
    assert comments[0]["post_id"] == created_comment["post_id"]
    assert comments[0]["id"] == created_comment["id"]


@pytest.mark.anyio
async def test_get_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get(f"/post/{created_post['id']}")
    assert response.status_code == 200
    data = response.json()
    assert "post" in data
    assert "comments" in data
    assert data["post"]["body"] == created_post["body"]
    assert data["post"]["id"] == created_post["id"]
    assert len(data["comments"]) == 1
    assert data["comments"][0]["body"] == created_comment["body"]
    assert data["comments"][0]["id"] == created_comment["id"]


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/999")
    assert response.status_code == 404
