from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth  # type: ignore
from google_auth_oauthlib.flow import Flow  # type: ignore
from sqlmodel import Session

from core.authentication import firebase_app, google_flow
from core.db import engine
from core.exception import InvalidToken
from models.user import FirebaseUser


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_google_auth_flow(request: Request) -> Flow:
    return google_flow(redirect_uri=request.url_for("auth_google"))


GoogleOAuthFlowDep = Annotated[Flow, Depends(get_google_auth_flow)]
security = HTTPBearer()


def get_firebase_user(
    token: HTTPAuthorizationCredentials = Depends(security),
) -> FirebaseUser:
    app = firebase_app()
    try:
        claims = auth.verify_id_token(
            token.credentials, app=app, check_revoked=True, clock_skew_seconds=10
        )
        return FirebaseUser(**claims)
    except Exception:
        raise InvalidToken()


FirebaseUserDep = Annotated[FirebaseUser, Depends(get_firebase_user)]
