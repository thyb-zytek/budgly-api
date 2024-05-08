from collections.abc import Generator
from typing import Any, ParamSpecKwargs

import pytest
from fastapi.testclient import TestClient
from jose import jwt
from pytest_mock.plugin import MockerFixture
from sqlmodel import Session, create_engine

from core.dependencies import get_db
from main import app
from models import SQLModel
from models.user import FirebaseUser
from tests.conftest import settings
from tests.factories import FirebaseTokenFactory, FirebaseTokenPayloadFactory


@pytest.fixture(scope="function", autouse=True)
def db() -> Generator[Session, None, None]:
    """Session for SQLAlchemy."""
    from .factories import BaseFactory

    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

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


class FirebaseTestClient:
    @classmethod
    def email_password_ok(cls, **kwargs: ParamSpecKwargs) -> Any:
        return FirebaseTokenFactory.create(
            **kwargs,
            payload__firebase__email=kwargs.get("email"),
            payload__firebase__sign_in_provider="password",
        ).model_dump(mode="json")

    @classmethod
    def email_password_fail(cls) -> str:
        return "ERROR"

    @classmethod
    def google_sign_in_ok(cls, **kwargs: ParamSpecKwargs) -> Any:
        return FirebaseTokenFactory.create(
            **kwargs,
            payload__firebase__sign_in_provider="google.com",
        ).model_dump(mode="json")


@pytest.fixture
def firebase_test_client() -> type[FirebaseTestClient]:
    return FirebaseTestClient


@pytest.fixture
def generate_token(mocker: MockerFixture) -> tuple[str, FirebaseUser]:
    payload = FirebaseTokenPayloadFactory.create()
    firebase_token = FirebaseTokenFactory.create(payload=payload)
    mock = mocker.patch("firebase_admin.auth.verify_id_token")
    mock.return_value = jwt.decode(
        firebase_token.idToken,
        key="secret_key",
        options={"verify_signature": False, "verify_aud": False},
    )
    return firebase_token.idToken, FirebaseUser(**payload.model_dump(mode="json"))
