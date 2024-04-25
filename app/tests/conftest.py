from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlmodel import Session, create_engine

from alembic.command import upgrade
from alembic.config import Config
from core.config import Settings
from core.dependencies import get_db
from main import app
from models import SQLModel

settings = Settings(POSTGRES_DB="test")
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
TestSession = Session(engine)


@pytest.fixture(scope="function", autouse=True)
def db() -> Generator[Session, None, None]:
    """Session for SQLAlchemy."""
    from .factories import BaseFactory

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for factory in BaseFactory.__subclasses__():
            factory.init_session(session)

        yield session

    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def get_test_db() -> Session:
        return db

    app.dependency_overrides[get_db] = get_test_db

    with TestClient(app) as client:
        yield client


def pytest_configure(config: pytest.Config) -> None:
    db_uri = str(settings.SQLALCHEMY_DATABASE_URI)
    if database_exists(db_uri):
        drop_database(db_uri)

    create_database(db_uri)

    with engine.begin() as connection:
        alembic_config = Config("alembic.ini")
        if connection is not None:
            alembic_config.attributes["connection"] = connection
        upgrade(alembic_config, "head")
