import logging
from collections.abc import Sequence

from fastapi import APIRouter
from starlette.status import HTTP_201_CREATED, HTTP_204_NO_CONTENT

from core.dependencies import FirebaseUserDep, SessionDep
from core.exceptions import NotFoundException
from crud.account import create_account, find_accounts
from crud.user import get_or_create_user
from models import Account, AccountCreate, AccountSerializer, AccountUpdate

router = APIRouter()
logger = logging.getLogger("budgly")


@router.get("/", response_model=list[AccountSerializer])
async def list_accounts(
    user: FirebaseUserDep, session: SessionDep
) -> Sequence[Account]:
    results = await find_accounts(session, user.uid)
    return results.all()


@router.post("/", response_model=AccountSerializer, status_code=HTTP_201_CREATED)
async def create(
    payload: AccountCreate, user: FirebaseUserDep, session: SessionDep
) -> Account:
    user = await get_or_create_user(session, user)
    account = await create_account(session, payload, user)
    return account


@router.patch("/{account_id}", response_model=AccountSerializer)
async def update(
    account_id: int, payload: AccountUpdate, user: FirebaseUserDep, session: SessionDep
) -> Account:
    results = await find_accounts(session, user.uid, account_id)
    account = results.one_or_none()
    if account is None:
        raise NotFoundException(f"Account(id: {account_id}) not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(account, key, value)

    session.add(account)
    await session.commit()
    await session.refresh(account)

    return account


@router.delete("/{account_id}", status_code=HTTP_204_NO_CONTENT)
async def delete_accounts(
    account_id: int, user: FirebaseUserDep, session: SessionDep
) -> None:
    results = await find_accounts(session, user.uid, account_id)
    account = results.one_or_none()
    if account is None:
        raise NotFoundException(f"Account(id: {account_id}) not found")

    await session.delete(account)
    await session.commit()
