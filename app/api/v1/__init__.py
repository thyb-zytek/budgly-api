from fastapi import APIRouter

from . import accounts, users

__version__ = 1

router = APIRouter()

router.include_router(users.router, tags=["V1|User"], prefix="/users")
router.include_router(accounts.router, tags=["V1|Account"], prefix="/accounts")
