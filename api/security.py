from datetime import datetime, timedelta
import logging

from fastapi import HTTPException
from sqlalchemy import select
from passlib.context import CryptContext
from jose import jwt

from api import config, database
from api.database import user_table
from api.models.user import User

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["bcrypt"])

def access_token_expires_minutes() -> int:
    return 30

def create_access_token(email: str) -> str:
    logger.debug("Creating access token", extra={"email": email})
    expire = datetime.utcnow() + timedelta(minutes=access_token_expires_minutes())
    jwt_data = {
        "sub": email,
        "exp": expire
    }
    encoded_jwt = jwt.encode(jwt_data, key=config.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

async def authenticate_user(email: str, password: str) -> User:
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

async def get_user(email: str):
    logger.debug("Getting user from database", extra={"email": email})
    query = select(user_table).where(user_table.c.email == email)
    logger.debug(query)
    result = await database.fetch_one(query)
    if result:
        return result