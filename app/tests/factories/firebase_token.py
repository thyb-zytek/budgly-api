from datetime import UTC, datetime, timedelta
from typing import Literal

import factory
import faker
from factory import fuzzy
from jose import jwt
from pydantic import BaseModel

from tests.factories import DefaultFactory

PROVIDERS = ["password", "google.com"]


class FirebaseProviderIdentity(BaseModel):
    sign_in_provider: Literal["password", "google.com"]
    identities: dict


class FirebaseProviderIdentityFactory(factory.Factory):
    class Meta:
        exclude = ("email",)
        model = FirebaseProviderIdentity

    sign_in_provider = fuzzy.FuzzyChoice(PROVIDERS)
    email = factory.Faker("email")

    @factory.lazy_attribute
    def identities(self):
        if self.sign_in_provider == "password":
            return {
                "email": [self.email],
            }

        faker.Faker.seed(0)

        return {
            self.sign_in_provider: [faker.Faker().ean(length=13)],
            "email": [self.email],
        }


class FirebaseTokenPayload(BaseModel):
    iss: str = "https://securetoken.google.com/budgly-tracker-app"
    aud: str = "budgly-tracker-app"
    auth_time: int
    user_id: str
    sub: str
    iat: int
    exp: int
    email: str
    email_verified: bool
    firebase: FirebaseProviderIdentity
    uid: str


class FirebaseTokenPayloadFactory(DefaultFactory):
    class Meta:
        model = FirebaseTokenPayload

    firebase = factory.SubFactory(FirebaseProviderIdentityFactory)
    auth_time = factory.lazy_attribute(
        lambda _: int((datetime.now(UTC) + timedelta(seconds=3600)).timestamp())
    )
    user_id = fuzzy.FuzzyText()
    uid = factory.SelfAttribute("user_id")
    sub = factory.SelfAttribute("user_id")
    iat = factory.SelfAttribute("auth_time")
    exp = factory.SelfAttribute("auth_time")
    email = factory.lazy_attribute(lambda item: item.firebase.identities["email"][0])
    email_verified = factory.lazy_attribute(
        lambda item: item.firebase.sign_in_provider == "google.com"
    )


class FirebaseToken(BaseModel):
    kind: str
    localId: str
    email: str
    displayName: str
    registered: bool
    expiresIn: int
    idToken: str
    refreshToken: str


class FirebaseTokenFactory(DefaultFactory):
    class Meta:
        model = FirebaseToken
        exclude = ("payload",)

    kind = "identitytoolkit#VerifyPasswordResponse"
    localId = fuzzy.FuzzyText()
    email = factory.lazy_attribute(lambda item: item.payload.email)
    displayName = factory.Faker("name")
    registered = True
    expiresIn = 3600
    payload = factory.SubFactory(FirebaseTokenPayloadFactory)
    idToken = factory.lazy_attribute(
        lambda item: jwt.encode(
            item.payload.model_dump(),
            "secret_key",
            algorithm="HS256",
        )
    )
    refreshToken = fuzzy.FuzzyText(length=80)
