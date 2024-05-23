from fastapi import HTTPException


class ServerError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=500, detail={"code": "SERVER_ERROR", "message": detail}
        )
