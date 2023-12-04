from threading import Thread
from typing import Type, Iterable, Any, Sequence, TypeVar

from pymongo.database import Database
from seriattrs import DbClass

from .DbClassOperator import DbClassOperator, NoSuchElementException
from .DbClassOperators import DbClassOperators

T = TypeVar('T', bound=DbClass)


class MongoDbOperator:
    def __init__(self, db: Database):
        self.db = db
        self._known_classes: dict[Type[T], DbClassOperator] = DbClassOperators(db)

    def delete(self, element: T) -> None:
        self._known_classes[type(element)].delete(element)

    def delete_by_id(self, element_class: Type[T], element_id: Any) -> None:
        self._known_classes[element_class].delete_by_id(element_id)

    def load(self, element_class: Type[T], element_id: Any) -> T:
        return self._known_classes[element_class].load(element_id)

    def load_multiple(self, element_class: Type[T], element_ids: Sequence[Any]) -> list[T]:
        results = [T for _ in element_ids]
        threads = tuple(
            Thread(target=lambda index, element_id: results.__setitem__(
                index, self._known_classes[element_class].load(element_id)),
                   args=(index, element_id)).start() for index, element_id in enumerate(element_ids))
        tuple(map(Thread.join, threads))
        return results

    def load_or_default(self, element_class: Type[T], element_id: Any, default=None) -> T:
        try:
            return self.load(element_class, element_id)
        except NoSuchElementException:
            return default

    def load_all(self, element_class: Type[T]) -> Iterable[T]:
        return self._known_classes[element_class].load_all()

    def update(self, element: T) -> T:
        return self._known_classes[type(element)].update(element)

    def write(self, element: T) -> T:
        return self._known_classes[type(element)].write(element)

    def clear_database(self):
        collection_names = self.db.list_collection_names()

        for collection_name in collection_names:
            collection = self.db[collection_name]
            collection.delete_many({})
