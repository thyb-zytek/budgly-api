import logging

from fastapi import APIRouter
from sqlalchemy import text

from core.dependencies import SessionDep

router = APIRouter()

logger = logging.getLogger("budgly")


@router.get("/healthcheck")
async def healthcheck(session: SessionDep) -> str:
    """Check if server is up and DB is reachable."""
    try:
        await session.exec(text("SELECT 1"))
    except Exception as e:
        logger.error(e)
        return "KO"
    return "OK"
