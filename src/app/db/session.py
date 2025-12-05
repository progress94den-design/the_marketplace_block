from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from src.app.db.config import settings

#############################################
# SYNC ENGINE (для Alembic и служебных задач)
#############################################

sync_engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    pool_pre_ping=True,
    echo=False,
    future=True,
)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


def get_sync_session():
    """Используется в Alembic или утилитах"""
    try:
        with SyncSessionLocal() as session:
            yield session
    finally:
        session.close()

# get_sync_session()
#############################################
# ASYNC ENGINE (для FastAPI)
#############################################

async_engine = create_async_engine(
    url=settings.DATABASE_URL_asyncpg,
    pool_pre_ping=True,  # Пингуем соединение с БД,защита от мертвых соединений
    echo=False,  # Включай True при отладке
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для FastAPI"""
    try:
        async with AsyncSessionLocal() as session:
            yield session
    finally:
        await session.close()
