from collections.abc import Generator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), future=True)


async def get_session() -> Generator[AsyncSession, None, None]:
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session


class BaseTable(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
