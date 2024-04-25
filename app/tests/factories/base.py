from typing import Any, Generic, TypeVar, get_args

from factory.alchemy import SQLAlchemyModelFactory
from factory.base import FactoryMetaClass
from faker import Faker
from sqlmodel import Session

T = TypeVar("T")

fake = Faker("fr_FR")


class BaseFactoryMeta(FactoryMetaClass):
    def __new__(
        mcs, class_name: str, bases: tuple[type], attrs: dict[str, Any]
    ) -> type:
        orig_bases = attrs.get("__orig_bases__", [])
        for t in orig_bases:
            if t.__name__ == "BaseFactory" and t.__module__ == __name__:
                type_args = get_args(t)
                if len(type_args) == 1:
                    if "Meta" not in attrs:
                        attrs["Meta"] = type("Meta", (), {})
                    attrs["Meta"].model = type_args[0]

        return super().__new__(mcs, class_name, bases, attrs)


class BaseFactory(Generic[T], SQLAlchemyModelFactory, metaclass=BaseFactoryMeta):
    class Meta:
        abstract = True

    @classmethod
    def init_session(cls, session: Session) -> None:
        cls._meta.sqlalchemy_session = session
        cls._meta.sqlalchemy_session_persistence = "commit"

    @classmethod
    def create(cls, **kwargs) -> T:
        return super().create(**kwargs)

    @classmethod
    def build(cls, **kwargs) -> T:
        return super().build(**kwargs)
