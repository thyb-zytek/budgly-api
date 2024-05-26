import logging
import random

from pydantic import BaseModel, HttpUrl, field_serializer
from sqlmodel import Field, Relationship, String, UniqueConstraint

from core.db import BaseTable
from models.extra import UserAccountLink
from models.user import User

logger = logging.getLogger("budgly")


def random_color_hex_code() -> str:
    def hex() -> int:
        return random.randint(0, 255)

    return f"#{hex():02X}{hex():02X}{hex():02X}"


class AccountCreate(BaseModel):
    name: str
    image: HttpUrl | None = None
    color: str | None = None

    @field_serializer("color")
    def serialize_color(self, value: str | None) -> str | None:
        if value is None and self.image is None:
            return random_color_hex_code()

        return value


class AccountUpdate(BaseModel):
    name: str | None = None
    image: HttpUrl | None = None
    color: str | None = None

    @field_serializer("color")
    def serialize_color(self, value: str | None) -> str | None:
        if value is None and "image" in self.model_fields_set and self.image is None:
            return random_color_hex_code()

        return value


class Account(BaseTable, table=True):
    name: str
    image: HttpUrl | None = Field(sa_type=String)
    color: str | None
    creator_id: str = Field(foreign_key="user.uid")

    creator: User = Relationship(back_populates="created_accounts")
    users: list[User] = Relationship(
        back_populates="accounts",
        link_model=UserAccountLink,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    __table_args__ = (
        UniqueConstraint(
            "creator_id",
            "name",
            name="unique_name_by_creator",
        ),
    )


class AccountSerializer(BaseTable):
    name: str
    image: HttpUrl | None = None
    color: str | None = None
    creator: User
