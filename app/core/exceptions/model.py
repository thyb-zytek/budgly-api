from fastapi import HTTPException


class NotFoundException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=404, detail={"code": "NOT_FOUND", "message": message}
        )


class ValidationException(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=400, detail={"code": "VALIDATION_ERROR", "message": message}
        )
