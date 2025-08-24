import pytest

@pytest.mark.anyio
async def register_user(async_client, email: str, password: str) -> dict:
    return await async_client.post("/register", json={"email": email, "password": password})

@pytest.mark.anyio
async def test_register_user(async_client):
    response = await register_user(async_client, "test@test.com", "test")
    assert response.status_code == 201
    assert "User registered successfully" in response.json()["detail"]

@pytest.mark.anyio
async def test_register_user_already_exists(async_client, registered_user):
    response = await register_user(async_client, registered_user["email"], "test")
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]