from collections.abc import Callable

import httpx
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockerFixture

from models.authentication import FirebaseToken, UserSignIn
from tests.conftest import settings
from tests.fixtures import FirebaseTestClient


def test_login_with_email(
    client: TestClient,
    mocker: MockerFixture,
    firebase_test_client: Callable[..., FirebaseTestClient],
) -> None:
    paylaod = UserSignIn(email="test@gmail.com", password="test")
    firebase_token = FirebaseTestClient.email_password_ok(**paylaod.model_dump())

    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=200,
        json=firebase_token,
        request=httpx.Request(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = client.post("/auth/login", json=paylaod.model_dump(mode="json"))
    assert response.status_code == 200
    assert isinstance(firebase_token, dict) is True
    assert response.json() == FirebaseToken(**firebase_token).model_dump(mode="json")


def tests_login_with_email_not_existing_account(
    client: TestClient,
    mocker: MockerFixture,
    firebase_test_client: Callable[..., FirebaseTestClient],
) -> None:
    payload = UserSignIn(email="test@gmail.com", password="test")
    mock = mocker.patch("httpx.post")
    mock.return_value = httpx.Response(
        status_code=400,
        json=FirebaseTestClient.email_password_fail(),
        request=httpx.Request(
            "POST",
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_APIKEY}",
        ),
    )

    response = client.post("/auth/login", json=payload.model_dump(mode="json"))

    assert response.status_code == 401
    assert response.json() == {
        "detail": {"code": "INVALID_CREDENTIALS", "message": "Invalid credentials"}
    }


def tests_login_with_email_not_valid_email(client: TestClient) -> None:
    response = client.post(
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


def test_google_authorization_url(client: TestClient) -> None:
    response = client.get("/auth/google")

    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "https://accounts.google.com/o/oauth2/auth?response_type=code" in data["url"]


def test_google_sign_in(
    client: TestClient,
    mocker: MockerFixture,
    firebase_test_client: Callable[..., FirebaseTestClient],
) -> None:
    firebase_token = FirebaseTestClient.google_sign_in_ok()

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

    response = client.get(
        "/auth/google/sign-in?code=code&state=state&scope=email+profile+openid&authuser=0&prompt=consent"
    )

    assert response.status_code == 200
    assert isinstance(firebase_token, dict) is True
    assert response.json() == FirebaseToken(**firebase_token).model_dump(mode="json")


def test_google_sign_in_fail_fetch_token(
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

    response = client.get(
        "/auth/google/sign-in?code=code&state=state&scope=email+profile+openid&authuser=0&prompt=consent"
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": {
            "code": "FIREBASE_ERROR",
            "message": "Something went wrong with Firebase",
        }
    }
