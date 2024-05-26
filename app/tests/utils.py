import sqlalchemy as sa
from sqlalchemy import TextClause
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


async def _get_scalar_result(engine: AsyncEngine, sql: TextClause) -> bool:
    try:
        async with engine.connect() as conn:
            return bool(await conn.scalar(sql))
    except Exception:
        return False


async def database_exists(url_str: str) -> bool:
    url = make_url(url_str)
    database = url.database
    engine = None
    try:
        text = f"SELECT 1 FROM pg_database WHERE datname='{database}'"
        for db in (database, "postgres", "template1", "template0", None):
            url = url._replace(database=db)
            engine = create_async_engine(url)
            try:
                return await _get_scalar_result(engine, sa.text(text))
            except (ProgrammingError, OperationalError):
                pass
        return False
    finally:
        if engine:
            await engine.dispose()


async def create_database(url_str: str) -> None:
    url = make_url(url_str)
    database = url.database
    url = url._replace(database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")

    template = "template1"
    async with engine.begin() as conn:
        text = f'CREATE DATABASE "{database}" ENCODING "utf8" TEMPLATE "{template}"'
        await conn.execute(sa.text(text))
    await engine.dispose()


async def drop_database(url_str: str) -> None:
    url = make_url(url_str)
    database = url.database
    url = url._replace(database="postgres")
    engine = create_async_engine(url, isolation_level="AUTOCOMMIT")
    async with engine.begin() as conn:
        # Disconnect all users from the database we are dropping.
        text = f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{database}'
            AND pid <> pg_backend_pid();
            """
        await conn.execute(sa.text(text))

        # Drop the database.
        text = f'DROP DATABASE "{database}"'
        await conn.execute(sa.text(text))
    await engine.dispose()
