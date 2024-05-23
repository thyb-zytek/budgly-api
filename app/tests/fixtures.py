import jwt
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pytest_mock.plugin import MockerFixture
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.dependencies import get_session
from main import app
from models import User
from tests.conftest import settings
from tests.factories import FirebaseTokenFactory


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        str(settings.SQLALCHEMY_DATABASE_URI), future=True, poolclass=NullPool
    )
    yield engine
    engine.sync_engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncSession:
    async with engine.begin() as connection:
        session_maker = async_sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
        )
        async with session_maker(bind=connection) as session:
            yield session
            # await session.flush()
            # await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_session] = _override_get_db

    async with LifespanManager(app) as manager:
        async with AsyncClient(
            transport=ASGITransport(app=manager.app), base_url="http://test"
        ) as ac:
            yield ac


@pytest_asyncio.fixture
def generate_token(mocker: MockerFixture) -> tuple[str, User]:
    firebase_token = FirebaseTokenFactory.create()
    mock = mocker.patch("firebase_admin.auth.verify_id_token")
    payload = jwt.decode(
        firebase_token.idToken,
        key="secret_key",
        options={"verify_signature": False, "verify_aud": False},
    )
    mock.return_value = payload
    return firebase_token.idToken, User(**payload)
