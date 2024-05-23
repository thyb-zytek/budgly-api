from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import logfire
from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api import authentication, main, v1
from core.authentication import firebase_app
from core.config import settings
from core.logging import setup_logging


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    firebase_app()

    application.include_router(main.router, tags=["Utilities"])
    application.include_router(
        authentication.router, tags=["Authentication"], prefix="/auth"
    )
    application.include_router(
        v1.router, tags=["V1"], prefix=f"{settings.API_STR}{v1.__version__}"
    )

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    debug=settings.DEBUG,
    version=settings.VERSION,
    lifespan=lifespan,
    swagger_ui_parameters={"deepLinking": False},
)

logfire.configure(console=False)
logfire.instrument_fastapi(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def exception_handler(
    request: Request, exc: RequestValidationError
) -> HTTPException:
    raise HTTPException(
        status_code=422,
        detail=[
            {
                "code": error["type"].upper(),
                "message": error["msg"],
                "location": error["loc"][-1] if error["loc"] else None,
            }
            for error in exc.errors()
        ],
    )
