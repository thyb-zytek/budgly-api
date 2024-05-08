from fastapi import HTTPException


class FirebaseAuthError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(
            status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": detail}
        )


class FirebaseException(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=500,
            detail={
                "code": "FIREBASE_ERROR",
                "message": "Something went wrong with Firebase",
            },
        )


class InvalidToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN",
                "message": "Invalid token",
            },
        )
