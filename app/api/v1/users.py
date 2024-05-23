from fastapi import APIRouter

from core.dependencies import FirebaseUserDep, SessionDep
from crud.user import get_or_create_user
from models.user import User

router = APIRouter()


@router.get("/me", response_model=User)
async def get_user(firebase_user: FirebaseUserDep, session: SessionDep) -> User:
    return await get_or_create_user(firebase_user, session)
