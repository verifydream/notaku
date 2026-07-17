"""Database connection — async SQLAlchemy + PostgreSQL."""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from settings import settings

engine = create_async_engine(settings.database_url, echo=False, pool_size=5)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy declarative models."""
    pass


async def get_db():
    """Dependency generator that provides a new database session.

    Yields:
        AsyncSession: An asynchronous SQLAlchemy session.
    """
    async with async_session() as session:
        yield session


async def init_db():
    """Initializes the database by creating all tables defined in Base.metadata.

    This should be called during the application startup lifecycle.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
