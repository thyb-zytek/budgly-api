from fastapi.testclient import TestClient
from pytest_mock import MockFixture


async def test_healthcheck(client: TestClient) -> None:
    response = await client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == "OK"


async def test_healthcheck_no_db(client: TestClient, mocker: MockFixture) -> None:
    mocker.patch(
        "sqlmodel.ext.asyncio.session.AsyncSession.exec", side_effect=Exception()
    )

    response = await client.get("/healthcheck")

    assert response.status_code == 200
    assert response.json() == "KO"
