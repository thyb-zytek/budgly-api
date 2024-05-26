import random

from polyfactory import Ignore

from models import Account, User
from tests.factories.base import BaseFactory


class UserFactory(BaseFactory[User]):
    uid: str = BaseFactory.__faker__.pystr(min_chars=28, max_chars=28)
    name: str = BaseFactory.__faker__.name() if bool(random.getrandbits(1)) else None
    email: str = BaseFactory.__faker__.email()

    accounts: list[Account] = Ignore()
    created_accounts: list[Account] = Ignore()
