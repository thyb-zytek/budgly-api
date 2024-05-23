import asyncio

from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import Settings
from models import SQLModel
from tests.utils import create_database, database_exists, drop_database

settings = Settings(POSTGRES_DB="test")

pytest_plugins = [
    "tests.fixtures",
]


async def prepare_db():
    db_url = str(settings.SQLALCHEMY_DATABASE_URI)

    async def _setup_db():
        if await database_exists(db_url):
            await drop_database(db_url)
        await create_database(db_url)

    await _setup_db()

    engine = create_async_engine(db_url, future=True, poolclass=NullPool)
    async with engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)

    engine.sync_engine.dispose()


def pytest_sessionstart(session):
    if getattr(session.config, "workerinput", None) is not None:
        return
    asyncio.run(prepare_db())
