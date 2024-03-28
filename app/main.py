from fastapi import FastAPI

from api import main

app = FastAPI(
    title="BUDGLY",
)

app.include_router(main.router)
