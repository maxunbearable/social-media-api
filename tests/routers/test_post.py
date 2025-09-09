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

async def like_post(async_client: AsyncClient, post_id: int, logged_in_token: str):
    response = await async_client.post(
        "/like",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"post_id": post_id},
    )
    return response


@pytest.fixture()
async def created_post(async_client: AsyncClient, logged_in_token: str):
    return await create_post("Test Post", async_client, logged_in_token)

@pytest.fixture()
async def created_comment(async_client: AsyncClient, created_post: dict, logged_in_token: str):
    return await create_comment("Test Comment", async_client, created_post, logged_in_token)

async def create_comment(body: str, async_client: AsyncClient, created_post: dict, logged_in_token: str):
    response = await async_client.post(
        "/comment",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": body, "post_id": created_post["id"]},
    )
    return response.json()


@pytest.mark.anyio
async def test_create_post(async_client: AsyncClient, logged_in_token: str, confirmed_user: dict):
    body = "Test Post"
    response = await async_client.post(
        "/post",
        headers={"Authorization": f"Bearer {logged_in_token}"},
        json={"body": body},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["body"] == body
    assert data["likes"] == 0
    assert data["user_id"] == confirmed_user["id"]
    assert "id" in data
    assert isinstance(data["id"], int)

@pytest.mark.anyio
async def test_create_post_expired_token(async_client: AsyncClient, confirmed_user: dict, mocker):
    mocker.patch("api.security.access_token_expires_minutes", return_value=-1)
    logged_in_token = security.create_access_token(confirmed_user["email"])
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
    assert posts[0]["likes"] == 0
    
@pytest.mark.anyio
@pytest.mark.parametrize(
    "sorting,expected_order", [
        ("new", [2, 1]),
        ("old", [1, 2]),
    ]
)
async def test_get_all_posts_sorting(async_client: AsyncClient, logged_in_token: str, sorting: str, expected_order: list[int]):
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    response = await async_client.get(f"/posts?sorting={sorting}")
    assert response.status_code == 200
    posts = response.json()
    post_ids = [post["id"] for post in posts]
    assert post_ids == expected_order
    
@pytest.mark.anyio
async def test_get_all_posts_sorting_by_likes(async_client: AsyncClient, logged_in_token: str):
    await create_post("Test Post 1", async_client, logged_in_token)
    await create_post("Test Post 2", async_client, logged_in_token)
    await like_post(async_client, 1, logged_in_token)
    response = await async_client.get("/posts?sorting=most_likes")
    assert response.status_code == 200
    posts = response.json()
    post_ids = [post["id"] for post in posts]
    assert post_ids == [1, 2]
    
@pytest.mark.anyio
async def test_get_all_posts_wrong_sorting(async_client: AsyncClient):
    response = await async_client.get("/posts?sorting=wrong")
    assert response.status_code == 422

@pytest.mark.anyio
async def test_create_comment(
    async_client: AsyncClient,
    created_post: dict,
    logged_in_token: str,
    confirmed_user: dict,
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
    assert data["user_id"] == confirmed_user["id"]
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
    assert "likes" in data["post"]
    assert data["post"]["body"] == created_post["body"]
    assert data["post"]["id"] == created_post["id"]
    assert data["post"]["likes"] == 0
    assert len(data["comments"]) == 1
    assert data["comments"][0]["body"] == created_comment["body"]
    assert data["comments"][0]["id"] == created_comment["id"]


@pytest.mark.anyio
async def test_get_missing_post_with_comments(
    async_client: AsyncClient, created_post: dict, created_comment: dict
):
    response = await async_client.get("/post/999")
    assert response.status_code == 404

@pytest.mark.anyio
async def test_like_post(async_client: AsyncClient, created_post: dict, logged_in_token: str, confirmed_user: dict):
    response = await like_post(async_client, created_post["id"], logged_in_token)
    assert response.status_code == 201
    data = response.json()
    assert data["post_id"] == created_post["id"]
    assert data["user_id"] == confirmed_user["id"]
    assert "id" in data
    assert isinstance(data["id"], int)
    
@pytest.mark.anyio
async def test_like_post_missing_post(async_client: AsyncClient, logged_in_token: str):
    response = await like_post(async_client, 999, logged_in_token)
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"