"""
Running in development environment: `fastapi dev ./backend`
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from arq import create_pool

from .routes import course_router, manage_router
from snatcher.conf import settings


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with await create_pool(settings.ARQ_REDIS_SETTINGS) as arq_redis:
        yield {'arq-redis': arq_redis}


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(course_router)
app.include_router(manage_router)
