import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from api.database import database, user_table
from api.models.user import UserIn
from api.security import authenticate_user, create_access_token, get_user, hash_password

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    query = user_table.insert().values(email=user.email, password=hash_password(user.password))
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User registered successfully"}

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}