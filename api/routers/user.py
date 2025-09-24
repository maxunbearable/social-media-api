import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from api import tasks
from api.database import database, user_table
from api.models.user import UserIn
from api.security import authenticate_user, create_access_token, create_confirmation_token, get_subject_for_token_type, get_user, hash_password

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserIn, request: Request):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    query = user_table.insert().values(email=user.email, password=hash_password(user.password), confirmed=False)
    logger.debug(query)
    await database.execute(query)
    await tasks.send_confirmation_email(user.email, request.url_for("confirm_email", token=create_confirmation_token(user.email)))
    return {"detail": "Please check your email for a confirmation link"}

@router.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = await authenticate_user(form_data.username, form_data.password)
    return {"access_token": create_access_token(user.email), "token_type": "bearer"}

@router.get("/confirm/{token}")
async def confirm_email(token: str):
    email = get_subject_for_token_type(token, "confirm")
    query = user_table.update().where(user_table.c.email == email).values(confirmed=True)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User confirmed successfully"}