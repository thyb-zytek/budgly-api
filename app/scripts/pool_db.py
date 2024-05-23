import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 20
wait_seconds = 2


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init(async_session: sessionmaker[Session]) -> None:
    async with async_session() as session:
        try:
            await session.exec(text("Select 1"))
        except Exception as e:
            logger.error(e)
            raise e


async def main() -> None:
    logger.info("Initializing service")
    await init(sessionmaker(engine, expire_on_commit=False, class_=AsyncSession))
    logger.info("Service finished initializing")


if __name__ == "__main__":
    asyncio.run(main())
