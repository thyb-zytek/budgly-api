import pytest
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlmodel import create_engine

from alembic.command import upgrade
from alembic.config import Config
from core.config import Settings

settings = Settings(POSTGRES_DB="test")
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

pytest_plugins = [
    "tests.fixtures",
]


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
