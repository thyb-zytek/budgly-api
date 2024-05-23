import logging

from rich.logging import Console, RichHandler

from core.config import settings


def setup_logging() -> None:
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    logger = logging.getLogger("budgly")
    console = Console()
    rich_handler = RichHandler(
        show_time=False,
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        markup=True,
        show_path=False,
        console=console,
    )

    rich_handler.setFormatter(
        logging.Formatter("[%(asctime)s] %(message)s", "%Y-%m-%d %H:%M:%S")
    )

    logger.addHandler(rich_handler)

    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    logger.propagate = False
