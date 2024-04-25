import logging

from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker
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
def init(session: sessionmaker[Session]) -> None:
    db = session()
    try:
        db.execute(text("Select 1"))
    except Exception as e:
        logger.error(e)
        raise e
    finally:
        db.close()


def main() -> None:
    logger.info("Initializing service")
    init(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
