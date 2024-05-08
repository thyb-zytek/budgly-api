from pydantic import BaseModel, EmailStr, HttpUrl


class FirebaseUser(BaseModel):
    uid: str
    email: EmailStr
    name: str | None = None
    picture: HttpUrl | None = None
