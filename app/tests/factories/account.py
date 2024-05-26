import random

from polyfactory import Ignore
from polyfactory.decorators import post_generated

from models import Account, User
from models.account import random_color_hex_code
from tests.factories.base import BaseFactory
from tests.factories.user import UserFactory


class AccountFactory(BaseFactory[Account]):
    id: int = Ignore()
    name: str = BaseFactory.__faker__.name()
    image: str | None = (
        BaseFactory.__faker__.url() if bool(random.getrandbits(1)) else None
    )

    @post_generated
    @classmethod
    def color(cls) -> str:
        return random_color_hex_code()

    @post_generated
    @classmethod
    def creator(cls) -> User:
        return UserFactory.build()

    @post_generated
    @classmethod
    def users(cls, creator: User) -> list[User]:
        users = [creator]
        if bool(random.getrandbits(1)):
            users.append(UserFactory.build())
        return users
