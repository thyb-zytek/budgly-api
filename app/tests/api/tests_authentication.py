import httpx
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockerFixture

from core.authentication import FirebaseToken, RefreshTokenPayload, UserSignIn
from tests.conftest import settings
from tests.factories import FirebaseRefreshTokenFactory, FirebaseTokenFactory


async def test_login_with_email(
    client: TestClient,
    mocker: MockerFixture,
) -> None:
    paylaod = UserSignIn(email="test@gmail.com", password="test")

    firebase_token = FirebaseTokenFactory.create(
        **paylaod.model_dump(mode="json"),
        provider="password",
    ).model_dump(mode="json")

    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=200,
        json=firebase_token,
        request=httpx.Request(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = await client.post("/auth/login", json=paylaod.model_dump(mode="json"))
    assert response.status_code == 200
    assert isinstance(firebase_token, dict) is True
    assert response.json() == FirebaseToken(**firebase_token).model_dump(mode="json")


async def tests_login_with_email_not_existing_account(
    client: TestClient,
    mocker: MockerFixture,
) -> None:
    payload = UserSignIn(email="test@gmail.com", password="test")
    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=400,
        json={},
        request=httpx.Request(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = await client.post("/auth/login", json=payload.model_dump(mode="json"))

    assert response.status_code == 401
    assert response.json() == {
        "detail": {"code": "INVALID_CREDENTIALS", "message": "Invalid credentials"}
    }


async def tests_login_with_email_not_valid_email(client: TestClient) -> None:
    response = await client.post(
        "/auth/login", json={"email": "test gmail.com", "password": "test"}
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "code": "VALUE_ERROR",
                "message": (
                    "value is not a valid email address: The email address is not valid. "
                    "It must have exactly one @-sign."
                ),
                "location": "email",
            }
        ]
    }


async def test_google_authorization_url(client: TestClient) -> None:
    response = await client.get("/auth/google")

    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "https://accounts.google.com/o/oauth2/auth?response_type=code" in data["url"]


async def test_google_sign_in(client: TestClient, mocker: MockerFixture) -> None:
    firebase_token = FirebaseTokenFactory.create(
        provider="google.com",
    ).model_dump(mode="json")

    mock_flow = mocker.patch("google_auth_oauthlib.flow.Flow.fetch_token")
    mock_flow.return_value = {"access_token": "token"}

    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=200,
        json=firebase_token,
        request=httpx.Request(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = await client.get(
        "/auth/google/sign-in?code=code&state=state&scope=email+profile+openid&authuser=0&prompt=consent"
    )

    mock_flow.assert_called_once()
    assert response.status_code == 200
    assert isinstance(firebase_token, dict) is True
    assert response.json() == FirebaseToken(**firebase_token).model_dump(mode="json")


async def test_google_sign_in_fail_fetch_token(
    client: TestClient, mocker: MockerFixture
) -> None:
    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=500,
        json={},
        request=httpx.Request(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = await client.get(
        "/auth/google/sign-in?code=code&state=state&scope=email+profile+openid&authuser=0&prompt=consent"
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "FIREBASE_ERROR",
            "message": "Something went wrong with Firebase",
        }
    }


async def test_refresh_token(client: TestClient, mocker: MockerFixture) -> None:
    firebase_refresh_token = FirebaseRefreshTokenFactory.create().model_dump(
        mode="json"
    )

    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=200,
        json=firebase_refresh_token,
        request=httpx.Request(
            "POST",
            f"https://securetoken.googleapis.com/v1/token?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = await client.post(
        "/auth/refresh",
        json=RefreshTokenPayload(
            refresh_token=firebase_refresh_token["refresh_token"]
        ).model_dump(),
    )

    assert response.status_code == 200
    assert response.json() == firebase_refresh_token


async def test_refresh_token_failed(client: TestClient, mocker: MockerFixture) -> None:
    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=500,
        json={},
        request=httpx.Request(
            "POST",
            f"https://securetoken.googleapis.com/v1/token?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = await client.post(
        "/auth/refresh",
        json=RefreshTokenPayload(refresh_token="test").model_dump(),
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": {"code": "INVALID_CREDENTIALS", "message": "Invalid refresh token"}
    }
