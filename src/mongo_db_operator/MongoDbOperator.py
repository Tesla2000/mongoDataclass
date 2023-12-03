from typing import Type, Iterable, TypeVar

from pymongo.database import Database
from seriattrs import DbClass
from .DbClassOperator import DbClassOperator, NoSuchElementException
from .DbClassOperators import DbClassOperators

T = TypeVar("T", bound=DbClass)


class MongoDbOperator:
    def __init__(self, db: Database):
        self.known_classes: dict[Type[DbClass], DbClassOperator] = DbClassOperators(db)

    def delete(self, element: DbClass):
        self.known_classes[type(element)].delete(element)

    def load(self, element_class: T, element_id: str) -> T:
        return self.known_classes[element_class].load(element_id)

    def load_or_default(self, element_class: T, element_id: str, default=None) -> T:
        try:
            return self.load(element_class, element_id)
        except NoSuchElementException:
            return default

    def load_all(self, element_class: Type[T]) -> Iterable[T]:
        return self.known_classes[element_class].load_all()

    def update(self, element: T) -> T:
        return self.known_classes[type(element)].update(element)

    def write(self, element: T) -> T:
        return self.known_classes[type(element)].write(element)
