from fastapi import Request
import pytest

@pytest.mark.anyio
async def register_user(async_client, email: str, password: str) -> dict:
    return await async_client.post("/register", json={"email": email, "password": password})

@pytest.mark.anyio
async def test_register_user(async_client):
    response = await register_user(async_client, "test@test.com", "test")
    assert response.status_code == 201
    assert "Please check your email for a confirmation link" in response.json()["detail"]

@pytest.mark.anyio
async def test_register_user_already_exists(async_client, registered_user):
    response = await register_user(async_client, registered_user["email"], "test")
    assert response.status_code == 400
    assert "Email already registered" in response.json()["detail"]
    
@pytest.mark.anyio
async def test_login_user(async_client, registered_user):
    response = await async_client.post("/token", data={"username": registered_user["email"], "password": "test"})
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"
    
@pytest.mark.anyio
async def test_login_user_invalid_credentials(async_client):
    response = await async_client.post("/token", data={"username": "test@test.com", "password": "test"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]
    
@pytest.mark.anyio
async def test_confirm_email(async_client, mocker):
    spy = mocker.spy(Request, "url_for")
    await register_user(async_client, "test@test.com", "test")
    confirmation_url = str(spy.spy_return)
    response = await async_client.get(confirmation_url)
    assert response.status_code == 200
    assert "User confirmed successfully" in response.json()["detail"]
    
@pytest.mark.anyio
async def test_confirm_email_invalid_token(async_client):
    response = await async_client.get("/confirm/invalid_token")
    assert response.status_code == 401
    assert "Invalid token" in response.json()["detail"]