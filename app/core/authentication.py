import logging
from functools import lru_cache
from typing import Annotated

import firebase_admin  # type: ignore
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth
from google_auth_oauthlib.flow import Flow  # type: ignore
from pydantic import BaseModel, EmailStr, Field, HttpUrl
from starlette.datastructures import URL

from core.config import settings
from core.exceptions import ExpiredToken, InvalidToken, ServerError
from models import User

logger = logging.getLogger("budgly")


class UserSignIn(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=1)]


class FirebaseToken(BaseModel):
    user_id: str = Field(..., alias="localId")
    token: str = Field(..., alias="idToken")
    refresh_token: str = Field(..., alias="refreshToken")
    email: EmailStr
    name: str = Field(..., alias="displayName")


class RefreshToken(BaseModel):
    id_token: str
    refresh_token: str


class GoogleAuthorizationUrl(BaseModel):
    url: HttpUrl


class RefreshTokenPayload(BaseModel):
    refresh_token: Annotated[str, Field(min_length=1)]


@lru_cache
def firebase_app() -> firebase_admin.App:
    cred = firebase_admin.credentials.Certificate(settings.FIREBASE_SA_KEYS_FILE)
    return firebase_admin.initialize_app(cred)


def google_flow(redirect_uri: URL) -> Flow:
    return Flow.from_client_secrets_file(
        settings.GOOGLE_OAUTH_SECRET_FILE,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
            "openid",
        ],
        redirect_uri=redirect_uri,
    )


def get_google_auth_flow(request: Request) -> Flow:
    return google_flow(redirect_uri=request.url_for("auth_google"))


security = HTTPBearer()

TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


def get_firebase_user(token: TokenDep) -> User:
    app = firebase_app()
    try:
        claims = auth.verify_id_token(
            token.credentials, app=app, check_revoked=True, clock_skew_seconds=10
        )
        return User(**claims)
    except auth.ExpiredIdTokenError:
        raise ExpiredToken()
    except auth.InvalidIdTokenError:
        raise InvalidToken()
    except Exception as e:
        logger.error(e)
        raise ServerError(message=str(e))
