import logging
from typing import Annotated

from fastapi import Depends
from google_auth_oauthlib.flow import Flow  # type: ignore
from sqlmodel.ext.asyncio.session import AsyncSession

from core.authentication import get_firebase_user, get_google_auth_flow
from core.db import get_session
from models import User

logger = logging.getLogger("budgly")


SessionDep = Annotated[AsyncSession, Depends(get_session)]

GoogleOAuthFlowDep = Annotated[Flow, Depends(get_google_auth_flow)]

FirebaseUserDep = Annotated[User, Depends(get_firebase_user)]
