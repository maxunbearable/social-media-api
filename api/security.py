from datetime import datetime, timedelta
import logging
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from passlib.context import CryptContext
from jose import ExpiredSignatureError, JWTError, jwt

from api.database import database, user_table
from api.config import get_config
from api.models.user import User

logger = logging.getLogger(__name__)

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
    encoded_jwt = jwt.encode(jwt_data, key=get_config().SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)

async def authenticate_user(email: str, password: str) -> User:
    logger.debug("Authenticating user", extra={"email": email})
    user = await get_user(email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Bearer"})
    return user

async def get_user(email: str):
    logger.debug("Getting user from database", extra={"email": email})
    query = select(user_table).where(user_table.c.email == email)
    logger.debug(query)
    result = await database.fetch_one(query)
    if result:
        return result
    
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, key=get_config().SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
        user = await get_user(email)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
        return user
    except ExpiredSignatureError as e:
        raise HTTPException(status_code=401, detail="Token expired", headers={"WWW-Authenticate": "Bearer"}) from e
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"}) from e