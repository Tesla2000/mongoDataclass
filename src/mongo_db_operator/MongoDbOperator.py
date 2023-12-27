from pathlib import Path
from typing import Type, Iterable, Any, Sequence, TypeVar
from warnings import warn

from pymongo.database import Database
from seriattrs import DbClass

from .DbClassOperator import NoSuchElementException
from .DbClassOperators import DbClassOperators

T = TypeVar('T', bound=DbClass)


class MongoDbOperator:
    def __init__(self, db: Database):
        self.db = db
        self._known_classes = DbClassOperators(db)

    def delete(self, element: T) -> None:
        self._known_classes[type(element)].delete(element)

    def delete_by_id(self, element_class: Type[T], element_id: Any) -> None:
        self._known_classes[element_class].delete_by_id(element_id)

    def load(self, element_class: Type[T], element_id: Any) -> T:
        return self._known_classes[element_class].load(element_id)

    def load_multiple(self, element_class: Type[T], element_ids: Sequence[Any]) -> list[T]:
        return self._known_classes[element_class].load_multiple(element_ids)

    def load_or_default(self, element_class: Type[T], element_id: Any, default=None) -> T:
        try:
            return self.load(element_class, element_id)
        except NoSuchElementException:
            return default

    def conv_to_dbclass(self, element_class: Type[T], doc) -> T:
        return self._known_classes[element_class].conv_to_dbclass(doc)

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

    def export_as_json(self, path: Path, exported_classes: list[Type[DbClass]] = None):
        if not path.is_dir():
            raise ValueError(f"{path=} you are trying to export data to is not a directory")
        if exported_classes is None:
            exported_classes = self._known_classes.keys()
        for exported_class in exported_classes:
            if exported_class not in self._known_classes:
                warn(f"{exported_class=} not in database. Skipping.")
                continue
            export_path = path.joinpath(exported_class.__name__).with_suffix('.json')
            operator = self._known_classes[exported_class]
            operator.export_as_json(export_path)

    def load_from_json(self, path: Path, imported_classes: list[Type[DbClass]] = None):
        if not path.is_dir():
            raise ValueError(f"{path=} you are trying to export data to is not a directory")
        if imported_classes is None:
            imported_classes = self._known_classes.keys()
        for imported_class in imported_classes:
            if imported_class not in self._known_classes:
                warn(f"{imported_class=} not in database. Skipping.")
                continue
            export_path = path.joinpath(imported_class.__name__).with_suffix('.json')
            operator = self._known_classes[imported_class]
            operator.load_from_json(export_path)
