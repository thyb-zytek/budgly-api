from httpx import AsyncClient
from pytest_mock import MockFixture


async def test_healthcheck(client: AsyncClient) -> None:
    response = await client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == "OK"


async def test_healthcheck_no_db(client: AsyncClient, mocker: MockFixture) -> None:
    mocker.patch(
        "sqlmodel.ext.asyncio.session.AsyncSession.exec", side_effect=Exception()
    )

    response = await client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == "KO"
