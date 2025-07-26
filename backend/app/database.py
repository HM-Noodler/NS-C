from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator
import logging

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

if settings.environment == "local":
    db_url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@127.0.0.1:5432/{settings.db_name}"
else:
    db_url = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@/{settings.db_name}?host=/cloudsql/{settings.db_connection_name}"

engine = create_async_engine(db_url)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db_and_tables() -> None:
    """Create the database and tables if they do not exist."""
    async with engine.begin() as conn:
        # Create the database if it does not exist
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database and tables created successfully.")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session."""
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            logger.error("An error occurred while using the database session.")
            raise
        finally:
            await session.close()
