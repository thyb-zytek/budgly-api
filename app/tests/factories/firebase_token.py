from datetime import datetime, timedelta
from typing import Literal

import jwt
from polyfactory.decorators import post_generated
from polyfactory.factories.pydantic_factory import ModelFactory
from pydantic import BaseModel, EmailStr, Field

PROVIDERS = ["password", "google.com"]


class FirebaseToken(BaseModel):
    localId: str
    idToken: str
    refreshToken: str
    email: EmailStr
    displayName: str
    provider: Literal["password", "google.com"] = Field(exclude=True)


class FirebaseRefreshToken(BaseModel):
    id_token: str
    refresh_token: str


class FirebaseTokenFactory(ModelFactory[FirebaseToken]):
    refreshToken: str = ModelFactory.__faker__.pystr(min_chars=80, max_chars=80)
    displayName: str = ModelFactory.__faker__.name()
    provider: str = ModelFactory.__faker__.random_element(elements=PROVIDERS)

    @post_generated
    @classmethod
    def idToken(cls, email: str, provider: str, localId: str) -> str:
        auth_time = int((datetime.now() + timedelta(seconds=3600)).timestamp())

        identities = {
            "email": [email],
        }
        if provider == "google.com":
            identities[provider] = [cls.__faker__.ean(length=13)]

        return jwt.encode(
            {
                "iss": "https://securetoken.google.com/budgly-tracker-app",
                "aud": "budgly-tracker-app",
                "auth_time": auth_time,
                "user_id": localId,
                "sub": localId,
                "iat": auth_time,
                "exp": auth_time,
                "email": email,
                "email_verified": provider == "google.com",
                "firebase": {
                    "identities": identities,
                    "sign_in_provider": provider,
                },
                "uid": localId,
            },
            "secret_key",
            algorithm="HS256",
        )
