import logging

from sqlalchemy import ScalarResult
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from core.exceptions import ValidationException
from models import Account, AccountCreate, User

logger = logging.getLogger("budgly")


async def find_accounts(
    session: AsyncSession, user_uid: str, account_id: int | None = None
) -> ScalarResult[Account]:
    query = select(Account).where(Account.users.any(User.uid == user_uid))  # type: ignore
    if account_id is not None:
        query = query.where(Account.id == account_id)
    result = await session.exec(query)
    return result


async def create_account(
    session: AsyncSession, payload: AccountCreate, user: User
) -> Account:
    try:
        account = Account(**payload.model_dump(mode="json"), creator=user)
        account.users.append(user)
        session.add(account)
        await session.commit()
        await session.refresh(account)
        return account
    except IntegrityError as e:
        logger.error(e)
        await session.rollback()
        if "UniqueViolationError" in str(e):
            raise ValidationException(f"Account name ({payload.name}) already exists")
        raise ValidationException("Failed to create account")
    except Exception as e:
        logger.error(e)
        raise ValidationException("Failed to validate account model")
