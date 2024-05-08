from fastapi import APIRouter

from . import users

__version__ = 1

router = APIRouter()

router.include_router(users.router, tags=["V1.User"], prefix="/users")
