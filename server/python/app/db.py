from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800)
SessionFactory = async_sessionmaker(engine, expire_on_commit=False)


async def db_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        yield session
