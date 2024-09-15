from typing import Generic, TypeVar

from faker import Faker
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

T = TypeVar("T")


class BaseFactory(SQLAlchemyFactory[T], ModelFactory[T], Generic[T]):
    __faker__ = Faker(locale="fr_FR")
    __is_base_factory__ = True
    __set_relationships__ = True
    __randomize_collection_length__ = True
    __min_collection_length__ = 3
