from typing import Any

import httpx
from fastapi import APIRouter, Request
from oauthlib.oauth2.rfc6749.errors import InvalidClientIdError, InvalidGrantError

from core.authentication import (
    FirebaseToken,
    GoogleAuthorizationUrl,
    RefreshToken,
    RefreshTokenPayload,
    UserSignIn,
)
from core.config import settings
from core.dependencies import GoogleOAuthFlowDep
from core.exceptions import FirebaseAuthError, FirebaseException

router = APIRouter()


@router.post("/login", response_model=FirebaseToken, response_model_by_alias=False)
async def login_with_email(payload: UserSignIn) -> Any:
    try:
        response = httpx.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_APIKEY}",
            data={"returnSecureToken": True, **payload.model_dump()},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError:
        raise FirebaseAuthError(message="Invalid credentials")


@router.get("/google")
async def login_with_google(flow: GoogleOAuthFlowDep) -> GoogleAuthorizationUrl:
    authorization_url, _ = flow.authorization_url(prompt="consent")
    return GoogleAuthorizationUrl(url=authorization_url)


@router.get(
    "/google/sign-in", response_model=FirebaseToken, response_model_by_alias=False
)
async def auth_google(code: str, flow: GoogleOAuthFlowDep, request: Request) -> Any:
    try:
        token = flow.fetch_token(code=code)
        response = httpx.post(
            f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={settings.FIREBASE_APIKEY}",
            data={
                "requestUri": request.url_for("auth_google"),
                "postBody": f"access_token={token["access_token"]}&providerId=google.com",
                "returnSecureToken": True,
                "returnIdpCredential": True,
            },
        )
        response.raise_for_status()
        return response.json()
    except (InvalidGrantError, InvalidClientIdError, httpx.HTTPStatusError):
        raise FirebaseException()


@router.post("/refresh", response_model=RefreshToken, response_model_by_alias=False)
async def refresh_token(payload: RefreshTokenPayload) -> Any:
    try:
        response = httpx.post(
            f"https://securetoken.googleapis.com/v1/token?key={settings.FIREBASE_APIKEY}",
            data={"grant_type": "refresh_token", **payload.model_dump()},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError:
        raise FirebaseAuthError(message="Invalid refresh token")
