from sqlalchemy.sql.functions import count
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from crud.user import get_or_create_user
from models import User
from tests.factories import UserFactory


async def test_get_or_create_user(db_session: AsyncSession) -> None:
    query = select(count()).select_from(User)
    user_payload = UserFactory.build()

    results = await db_session.exec(query)
    assert results.first() == 0

    user = await get_or_create_user(db_session, user_payload)
    assert user is not None
    assert user.uid == user_payload.uid

    results = await db_session.exec(query)
    assert results.first() == 1

    user = await get_or_create_user(db_session, user_payload)
    assert user is not None
    assert user.uid == user_payload.uid

    results = await db_session.exec(query)
    assert results.first() == 1

    user = await UserFactory.create_async()
    user = await get_or_create_user(db_session, user)
    assert user is not None
    assert user.uid == user.uid

    results = await db_session.exec(query)
    assert results.first() == 2
