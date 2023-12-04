from threading import Thread
from typing import Type, Iterable, Any, Sequence

from pymongo.database import Database
from seriattrs import DbClass

from .DbClassOperator import DbClassOperator, NoSuchElementException
from .DbClassOperators import DbClassOperators


class MongoDbOperator:
    def __init__(self, db: Database):
        self.known_classes: dict[Type[DbClass], DbClassOperator] = DbClassOperators(db)

    def delete(self, element: DbClass):
        self.known_classes[type(element)].delete(element)

    def load[T](self, element_id: Any) -> T:
        return self.known_classes[T].load(element_id)

    def load_multiple[T](self, element_ids: Sequence[Any]) -> list[T]:
        results = [T for _ in element_ids]
        threads = tuple(
            Thread(target=lambda index, element_id: results.__setitem__(
                index, self.known_classes[T].load(element_id)),
                   args=(index, element_id)).start() for index, element_id in enumerate(element_ids))
        tuple(map(Thread.join, threads))
        return results

    def load_or_default[T](self, element_id: Any, default=None) -> T:
        try:
            return self.load[T](element_id)
        except NoSuchElementException:
            return default

    def load_all[T](self) -> Iterable[T]:
        return self.known_classes[T].load_all()

    def update(self, element: DbClass) -> None:
        self.known_classes[type(element)].update(element)

    def write(self, element: DbClass) -> None:
        self.known_classes[type(element)].write(element)
