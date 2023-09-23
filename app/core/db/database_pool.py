from psycopg_pool.pool_async import AsyncConnectionPool, AsyncConnection
from fastapi import FastAPI, Request
from app.core.configs import get_logger, get_environment
from contextlib import asynccontextmanager
from .pg_connection import PGConnection

_env = get_environment()
_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _logger.info("Starting pool")
    app.async_pool = AsyncConnectionPool(
        conninfo=(
            f"host={_env.DATABASE_HOST} "
            f"port={_env.DATABASE_PORT} "
            f"user={_env.DATABASE_USER} "
            f"password={_env.DATABASE_PASSWORD} "
            f"dbname={_env.DATABASE_NAME}"),
        min_size=_env.DATABASE_MIN_CONNECTIONS,
        max_size=_env.DATABASE_MAX_CONNECTIONS,
        timeout=None
    )
    yield

    _logger.info("Closing pool")
    await app.async_pool.close()

async def get_connection(request: Request) -> AsyncConnection:
    async with request.app.async_pool.connection() as conn:
        yield PGConnection(conn=conn)
