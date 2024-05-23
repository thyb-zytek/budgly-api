from sqlmodel import Session

from models import User


async def get_or_create_user(user_in: User, session: Session) -> User:
    user = await session.get(User, user_in.uid)
    if user is None:
        user = user_in
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user
