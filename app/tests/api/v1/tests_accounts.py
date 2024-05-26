from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from models import Account, User
from tests.factories import AccountFactory, UserFactory


async def tests_list_accounts(
    client: AsyncClient, generate_token: tuple[str, User]
) -> None:
    token, user = generate_token
    user = await UserFactory.create_async(**user.model_dump(mode="json"))
    accounts = await AccountFactory.create_batch_async(2, creator=user)

    response = await client.get(
        "/api/v1/accounts/", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    assert len(response.json()) == len(accounts)


async def test_create_account(
    client: AsyncClient, generate_token: tuple[str, User], db_session: AsyncSession
) -> None:
    token, user = generate_token
    user = await UserFactory.create_async(**user.model_dump(mode="json"))

    response = await client.post(
        "/api/v1/accounts/",
        json={"name": "Test Account"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["creator"]["uid"] == user.uid
    account = await db_session.get(Account, data["id"])
    assert account is not None
    assert account.name == data["name"]
    assert account.creator_id == user.uid


async def test_update_account(
    client: AsyncClient, generate_token: tuple[str, User], db_session: AsyncSession
) -> None:
    token, user = generate_token
    user = await UserFactory.create_async(**user.model_dump(mode="json"))
    account = await AccountFactory.create_async(creator=user)

    response = await client.patch(
        f"/api/v1/accounts/{account.id}",
        json={"name": "Updated Account"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Account"
    account = await db_session.get(Account, data["id"])
    assert account is not None
    assert account.name == data["name"]


async def test_update_account_not_found(
    client: AsyncClient, generate_token: tuple[str, User]
) -> None:
    token, user = generate_token

    response = await client.patch(
        "/api/v1/accounts/999",
        json={"name": "Updated Account"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {"code": "NOT_FOUND", "message": "Account(id: 999) not found"}
    }


async def test_delete_account(
    client: AsyncClient, generate_token: tuple[str, User], db_session: AsyncSession
) -> None:
    token, user = generate_token
    user = await UserFactory.create_async(**user.model_dump(mode="json"))
    account = await AccountFactory.create_async(creator=user)

    response = await client.delete(
        f"/api/v1/accounts/{account.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 204
    account = await db_session.get(Account, account.id)
    assert account is None


async def test_delete_account_not_found(
    client: AsyncClient, generate_token: tuple[str, User]
) -> None:
    token, user = generate_token

    response = await client.delete(
        "/api/v1/accounts/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": {"code": "NOT_FOUND", "message": "Account(id: 999) not found"}
    }
