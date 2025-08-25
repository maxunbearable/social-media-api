import logging
from fastapi import APIRouter, HTTPException, status

from api.database import database, user_table
from api.models.user import UserIn
from api.security import authenticate_user, create_access_token, get_user, hash_password

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register")
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    query = user_table.insert().values(email=user.email, password=hash_password(user.password))
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User registered successfully"}

@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}