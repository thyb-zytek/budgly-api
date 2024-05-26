from sqlmodel import Field, Relationship, SQLModel

from models.extra import UserAccountLink

if False:
    from .account import Account


class User(SQLModel, table=True):
    uid: str = Field(primary_key=True)
    name: str | None = None
    email: str

    accounts: list["Account"] = Relationship(
        back_populates="users",
        link_model=UserAccountLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    created_accounts: list["Account"] | None = Relationship(back_populates="creator")
