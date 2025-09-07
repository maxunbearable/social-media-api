from fastapi import HTTPException
import pytest
from jose import jwt

from api.config import get_config
from api.security import ALGORITHM, access_token_expires_minutes, authenticate_user, confirm_token_expires_minutes, create_access_token, create_confirmation_token, get_current_user, get_user, hash_password, verify_password

@pytest.mark.anyio
async def test_get_user(registered_user):
    user = await get_user(registered_user["email"])
    assert user.email == registered_user["email"]

@pytest.mark.anyio
async def test_get_user_not_found():
    user = await get_user("not_found@test.com")
    assert user is None
    
@pytest.mark.anyio
async def test_hash_password():
    password = "test"
    hashed_password = hash_password(password)
    assert hashed_password is not None
    assert verify_password(password, hashed_password)
    
@pytest.mark.anyio
async def test_create_access_token():
    email = "test@test.com"
    token = create_access_token(email)
    assert {"sub": email, "type": "access"}.items() <= jwt.decode(token, key=get_config().SECRET_KEY, algorithms=[ALGORITHM]).items()
    
@pytest.mark.anyio
async def test_create_confirmation_token():
    email = "test@test.com"
    token = create_confirmation_token(email)
    assert {"sub": email, "type": "confirm"}.items() <= jwt.decode(token, key=get_config().SECRET_KEY, algorithms=[ALGORITHM]).items()
    
@pytest.mark.anyio
def test_access_token_expires_minutes():
    assert access_token_expires_minutes() == 30
    
@pytest.mark.anyio
def test_confirm_token_expires_minutes():
    assert confirm_token_expires_minutes() == 1440
    
@pytest.mark.anyio
async def test_authenticate_user(registered_user):
    user = await authenticate_user(registered_user["email"], "test")
    assert user.email == registered_user["email"]
    
@pytest.mark.anyio
async def test_authenticate_user_invalid_credentials():
    with pytest.raises(HTTPException) as e:
        await authenticate_user("test@test.com", "invalid")
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid credentials"
    
@pytest.mark.anyio
async def test_authenticate_user_not_found():
    with pytest.raises(HTTPException) as e:
        await authenticate_user("not_found@test.com", "test")
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid credentials"
    
@pytest.mark.anyio
async def test_get_current_user(registered_user):
    token = create_access_token(registered_user["email"])
    user = await get_current_user(token)
    assert user.email == registered_user["email"]
    
@pytest.mark.anyio
async def test_get_current_user_invalid_token():
    with pytest.raises(HTTPException) as e:
        await get_current_user("invalid")
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid token"
    
@pytest.mark.anyio
async def test_get_current_user_wrong_token_type():
    token = create_confirmation_token("test@test.com")
    with pytest.raises(HTTPException) as e:
        await get_current_user(token)
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid token"