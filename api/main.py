from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, Request
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.exceptions import HTTPException
from api.database import database
from api.logging_conf import configure_logging
from api.routers.post import router as post_router
from api.routers.user import router as user_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware,)

app.include_router(post_router)
app.include_router(user_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.status_code} {exc.detail}")
    return await http_exception_handler(request, exc)