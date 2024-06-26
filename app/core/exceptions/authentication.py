from fastapi import HTTPException


class FirebaseAuthError(HTTPException):
    def __init__(self, message: str) -> None:
        super().__init__(
            status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": message}
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


class ExpiredToken(HTTPException):
    def __init__(self) -> None:
        super().__init__(
            status_code=401,
            detail={
                "code": "EXPIRED_TOKEN",
                "message": "Token expired",
            },
        )
