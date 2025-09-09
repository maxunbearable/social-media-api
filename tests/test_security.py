from fastapi import HTTPException
import pytest
from jose import jwt

from api.config import get_config
from api.security import ALGORITHM, access_token_expires_minutes, authenticate_user, confirm_token_expires_minutes, create_access_token, create_confirmation_token, get_current_user, get_subject_for_token_type, get_user, hash_password, verify_password

@pytest.mark.anyio
async def test_get_user(confirmed_user):
    user = await get_user(confirmed_user["email"])
    assert user.email == confirmed_user["email"]

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
async def test_authenticate_user(confirmed_user):
    user = await authenticate_user(confirmed_user["email"], "test")
    assert user.email == confirmed_user["email"]
    
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
async def test_get_current_user(confirmed_user):
    token = create_access_token(confirmed_user["email"])
    user = await get_current_user(token)
    assert user.email == confirmed_user["email"]
    
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
    assert e.value.detail == "Invalid token type, expected access"

@pytest.mark.anyio
async def test_get_subject_for_token_confirm():
    token = create_confirmation_token("test@test.com")
    email = get_subject_for_token_type(token, "confirm")
    assert email == "test@test.com"
    
@pytest.mark.anyio
async def test_get_subject_for_token_access():
    token = create_access_token("test@test.com")
    email = get_subject_for_token_type(token, "access")
    assert email == "test@test.com"
    
@pytest.mark.anyio
async def test_get_subject_for_token_invalid_token_type():
    token = create_access_token("test@test.com")
    with pytest.raises(HTTPException) as e:
        get_subject_for_token_type(token, "invalid")
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid token type, expected invalid"
    
@pytest.mark.anyio
async def test_get_subject_for_token_invalid_token():
    token = "Invalid token"
    with pytest.raises(HTTPException) as e:
        get_subject_for_token_type(token, "access")
    assert e.value.status_code == 401
    assert e.value.detail == "Invalid token"

@pytest.mark.anyio
async def test_get_subject_for_token_type_expired(mocker):
    mocker.patch("api.security.access_token_expires_minutes", return_value=-1)
    token = create_access_token("test@test.com")
    with pytest.raises(HTTPException) as e:
        get_subject_for_token_type(token, "access")
    assert e.value.status_code == 401
    assert e.value.detail == "Token has expired"

@pytest.mark.anyio
async def test_get_subject_for_token_type_missing_token_subject():
    token = create_access_token("test@test.com")
    payload = jwt.decode(token, key=get_config().SECRET_KEY, algorithms=[ALGORITHM])
    del payload["sub"]
    token = jwt.encode(payload, key=get_config().SECRET_KEY, algorithm=ALGORITHM)
    with pytest.raises(HTTPException) as e:
        get_subject_for_token_type(token, "access")
    assert e.value.status_code == 401
    assert e.value.detail == "Token subject is missing"