import pytest

from api.security import get_user, hash_password, verify_password

@pytest.mark.anyio
async def test_get_user(register_user):
    user = await get_user(register_user["email"])
    assert user.email == register_user["email"]

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