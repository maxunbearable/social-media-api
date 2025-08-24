import logging

from sqlalchemy import select

from api import database
from api.database import user_table

logger = logging.getLogger(__name__)

async def get_user(email: str):
    logger.debug("Getting user from database", extra={"email": email})
    query = select(user_table).where(user_table.c.email == email)
    logger.debug(query)
    result = await database.fetch_one(query)
    if result:
        return result