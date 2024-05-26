from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from models.user import User


async def test_users_get_me(
    client: AsyncClient, generate_token: tuple[str, User], db_session: AsyncSession
) -> None:
    token, user = generate_token
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == user.model_dump(mode="json")

    db_user = await db_session.get(User, user.uid)

    assert db_user is not None
    assert db_user.email == user.email


async def test_users_get_me_invalid_token(client: AsyncClient) -> None:
    response = await client.get(
        "/api/v1/users/me", headers={"Authorization": "Bearer token"}
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": {"code": "INVALID_TOKEN", "message": "Invalid token"}
    }
