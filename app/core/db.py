from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings

engine = create_async_engine(str(settings.SQLALCHEMY_DATABASE_URI), future=True)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSession(engine) as session:
        yield session


class BaseTable(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
