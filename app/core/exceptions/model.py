from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=401, detail={"code": "NOT_FOUND", "message": detail}
        )


class ValidationException(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=400, detail={"code": "VALIDATION_ERROR", "message": detail}
        )
