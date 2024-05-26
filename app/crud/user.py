from sqlmodel.ext.asyncio.session import AsyncSession

from models import User


async def get_or_create_user(session: AsyncSession, user_in: User) -> User:
    user = await session.get(User, user_in.uid)
    if user is None:
        user = user_in
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user
