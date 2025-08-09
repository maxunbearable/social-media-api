from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from api.database import database
from api.logging_conf import configure_logging
from api.routers.post import router as post_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.include_router(post_router)