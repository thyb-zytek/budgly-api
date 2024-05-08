from fastapi import APIRouter

from core.dependencies import FirebaseUserDep
from models.user import FirebaseUser

router = APIRouter()


@router.get("/me", response_model=FirebaseUser)
def get_firebase_user(user: FirebaseUserDep) -> FirebaseUser:
    return user
