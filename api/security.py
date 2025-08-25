import logging

from sqlalchemy import select
from passlib.context import CryptContext

from api import database
from api.database import user_table

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

async def get_user(email: str):
    logger.debug("Getting user from database", extra={"email": email})
    query = select(user_table).where(user_table.c.email == email)
    logger.debug(query)
    result = await database.fetch_one(query)
    if result:
        return result