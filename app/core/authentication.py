from functools import lru_cache

import firebase_admin  # type: ignore
from google_auth_oauthlib.flow import Flow  # type: ignore
from starlette.datastructures import URL

from core.config import settings


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
