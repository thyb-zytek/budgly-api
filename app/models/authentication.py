from pydantic import BaseModel, EmailStr, Field


class UserSignIn(BaseModel):
    email: EmailStr
    password: str


class FirebaseToken(BaseModel):
    user_id: str = Field(..., alias="localId")
    token: str = Field(..., alias="idToken")
    refresh_token: str = Field(..., alias="refreshToken")
    email: EmailStr
    name: str = Field(..., alias="displayName")


class GoogleAuthorizationUrl(BaseModel):
    url: str
