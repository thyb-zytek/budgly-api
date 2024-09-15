from sqlmodel import Session

from core.db import engine
from core.dependencies import get_db


def test_get_db() -> None:
    session = next(get_db())

    assert isinstance(session, Session) is True
    assert session.bind == engine
