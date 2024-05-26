import jwt
import pytest
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from firebase_admin import auth  # type: ignore
from pytest_mock import MockerFixture

from core.dependencies import get_firebase_user, get_google_auth_flow, get_session
from core.exceptions import ExpiredToken, InvalidToken, ServerError
from tests.factories import FirebaseTokenFactory


async def test_google_flow_dependencies(mocker: MockerFixture) -> None:
    request = mocker.MagicMock(
        spec=Request,
    )
    request.url_for.return_value = "http://localhost:3000"
    flow = get_google_auth_flow(request)

    assert flow.client_config["project_id"] == "budgly-tracker-app"


async def test_firebase_user_dependencies(mocker: MockerFixture) -> None:
    firebase_token = FirebaseTokenFactory.build()

    mock = mocker.patch("firebase_admin.auth.verify_id_token")
    mock.return_value = jwt.decode(
        firebase_token.idToken,
        key="secret_key",
        options={"verify_signature": False, "verify_aud": False},
    )

    token = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=firebase_token.idToken
    )

    user = get_firebase_user(token=token)
    assert user.email == firebase_token.email


async def test_firebase_user_dependencies_expired_token(mocker: MockerFixture) -> None:
    mock = mocker.patch("firebase_admin.auth.verify_id_token")
    mock.side_effect = auth.ExpiredIdTokenError(message="Expired", cause="test")

    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="Test")

    with pytest.raises(ExpiredToken) as exc_info:
        get_firebase_user(token)

    assert isinstance(exc_info.value, ExpiredToken) is True
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {
        "code": "EXPIRED_TOKEN",
        "message": "Token expired",
    }


async def test_firebase_user_dependencies_invalid_token(mocker: MockerFixture) -> None:
    mock = mocker.patch("firebase_admin.auth.verify_id_token")
    mock.side_effect = auth.InvalidIdTokenError(message="Invalid", cause="test")

    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="Test")

    with pytest.raises(InvalidToken) as exc_info:
        get_firebase_user(token)

    assert isinstance(exc_info.value, InvalidToken) is True
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == {
        "code": "INVALID_TOKEN",
        "message": "Invalid token",
    }


async def test_firebase_user_dependencies_exception(mocker: MockerFixture) -> None:
    mock = mocker.patch("firebase_admin.auth.verify_id_token")
    mock.side_effect = Exception("test")

    token = HTTPAuthorizationCredentials(scheme="Bearer", credentials="Test")

    with pytest.raises(ServerError) as exc_info:
        get_firebase_user(token)

    assert isinstance(exc_info.value, ServerError) is True
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == {"code": "SERVER_ERROR", "message": "test"}


async def test_session_dependencies() -> None:
    session = get_session()
    assert session is not None
