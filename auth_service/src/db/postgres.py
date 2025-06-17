from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.core.config import settings

Base = declarative_base()

dsn = (
    f"postgresql+asyncpg://{settings.pg_user}:{settings.pg_password}@"
    f"{settings.pg_host}:{settings.pg_port}/{settings.pg_name}"
)
engine = create_async_engine(dsn, echo=True, future=True)
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
