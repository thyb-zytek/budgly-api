from datetime import datetime, timedelta

import factory
import faker
import jwt
from factory import fuzzy
from pydantic import BaseModel, EmailStr

from tests.factories import DefaultFactory

PROVIDERS = ["password", "google.com"]


class FirebasePayloadToken(BaseModel):
    localId: str
    idToken: str
    refreshToken: str
    email: EmailStr
    displayName: str


class FirebaseTokenFactory(DefaultFactory):
    class Meta:
        model = FirebasePayloadToken
        exclude = ("provider",)

    localId = fuzzy.FuzzyText()
    refreshToken = fuzzy.FuzzyText(length=80)
    email = factory.Faker("email")
    displayName = factory.Faker("name")
    provider = fuzzy.FuzzyChoice(PROVIDERS)

    @factory.lazy_attribute
    def idToken(self):
        auth_time = int((datetime.now() + timedelta(seconds=3600)).timestamp())
        identities = {
            "email": [self.email],
        }
        if self.provider == "google.com":
            faker.Faker.seed(0)
            identities[self.provider] = [faker.Faker().ean(length=13)]

        return jwt.encode(
            {
                "iss": "https://securetoken.google.com/budgly-tracker-app",
                "aud": "budgly-tracker-app",
                "auth_time": auth_time,
                "user_id": self.localId,
                "sub": self.localId,
                "iat": auth_time,
                "exp": auth_time,
                "email": self.email,
                "email_verified": self.provider == "google.com",
                "firebase": {
                    "identities": identities,
                    "sign_in_provider": self.provider,
                },
                "uid": self.localId,
            },
            "secret_key",
            algorithm="HS256",
        )


class FirebaseRefreshToken(BaseModel):
    id_token: str
    refresh_token: str


class FirebaseRefreshTokenFactory(DefaultFactory):
    class Meta:
        model = FirebaseRefreshToken
        exclude = ("firebase_token",)

    firebase_token = factory.SubFactory(FirebaseTokenFactory)
    id_token = factory.lazy_attribute(lambda obj: obj.firebase_token.idToken)
    refresh_token = factory.lazy_attribute(lambda obj: obj.firebase_token.refreshToken)
