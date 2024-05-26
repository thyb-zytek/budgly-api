import pytest
from pytest_mock import MockFixture
from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from core.exceptions import ValidationException
from crud.account import create_account, find_accounts
from models import AccountCreate
from tests.factories import AccountFactory, UserFactory


async def test_find_accounts(db_session: AsyncSession) -> None:
    creator = await UserFactory.create_async()
    accounts = await AccountFactory.create_batch_async(size=2, creator=creator)

    results = await find_accounts(db_session, creator.uid)
    db_accounts = results.all()
    assert len(accounts) == 2
    assert db_accounts == accounts

    results = await find_accounts(db_session, creator.uid, accounts[0].id)
    db_account = results.one_or_none()
    assert db_account is not None
    assert db_account == accounts[0]

    result = await find_accounts(db_session, creator.uid, 0)
    db_account = result.one_or_none()
    assert db_account is None


async def test_create_account(db_session: AsyncSession) -> None:
    account = AccountFactory.build()
    user = await UserFactory.create_async()
    payload = AccountCreate.model_validate(account.model_dump())

    db_account = await create_account(db_session, payload, user)
    assert account is not None
    assert db_account.name == account.name
    assert db_account.image == account.image
    assert db_account.color == account.color
    assert db_account.id is not None


async def test_create_duplicate_account(db_session: AsyncSession) -> None:
    account = await AccountFactory.create_async()
    payload = AccountCreate(name=account.name)

    with pytest.raises(ValidationException) as exc_info:
        await create_account(db_session, payload, account.creator)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {
        "code": "VALIDATION_ERROR",
        "message": f"Account name ({payload.name}) already exists",
    }


async def test_create_account_db_raise(
    mocker: MockFixture, db_session: AsyncSession
) -> None:
    account = await AccountFactory.create_async()
    payload = AccountCreate(name=account.name)

    mocker.patch(
        "sqlmodel.ext.asyncio.session.AsyncSession.commit",
        side_effect=IntegrityError("error", None, Exception("error")),
    )

    with pytest.raises(ValidationException) as exc_info:
        await create_account(db_session, payload, account.creator)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {
        "code": "VALIDATION_ERROR",
        "message": "Failed to create account",
    }


async def test_create_account_model_raise(
    mocker: MockFixture, db_session: AsyncSession
) -> None:
    account = await AccountFactory.create_async()
    payload = AccountCreate(name=account.name)

    mocker.patch("pydantic.BaseModel.model_dump", side_effect=Exception)

    with pytest.raises(ValidationException) as exc_info:
        await create_account(db_session, payload, account.creator)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == {
        "code": "VALIDATION_ERROR",
        "message": "Failed to validate account model",
    }
