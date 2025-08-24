import logging
from fastapi import APIRouter, HTTPException, status

from api.database import database, user_table
from api.models.user import UserIn
from api.security import get_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register")
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    query = user_table.insert().values(email=user.email, password=user.password)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User registered successfully"}