import csv
from pathlib import Path
from threading import Thread
from typing import Type, Any, Iterable, TypeVar, Sequence

from pymongo.database import Database
from seriattrs import DbClass

T = TypeVar('T', bound=DbClass)


class DbClassOperator:
    def __init__(self, db: Database, operated_class: Type[T]):
        self.db = db
        if not issubclass(operated_class, DbClass):
            raise ValueError("Operated class {} must be a subclass of DbClass".format(operated_class))
        self.operated_class = operated_class
        self.collection_name = operated_class.__name__
        self.collection = self.db[self.collection_name]

    def delete(self, element: T) -> None:
        result = self.collection.delete_one({"_id": element._id})
        if result.deleted_count != 1:
            raise NoSuchElementException("No element {} present in the database".format(element))
        del element

    def delete_by_id(self, element_id: Any) -> None:
        result = self.collection.delete_one({"_id": element_id})
        if result.deleted_count != 1:
            raise NoSuchElementException("No element with element_id {} present in the database".format(element_id))

    def load(self, object_id: Any) -> T:
        document = self.collection.find_one({"_id": object_id})
        if not document:
            raise NoSuchElementException(
                "No element with _id={} in the collection_name={}".format(object_id, self.collection_name)
            )
        return self.conv_to_dbclass(document)

    def load_multiple(self, element_ids: Sequence[Any]) -> list[T]:
        results = [T for _ in element_ids]
        threads = tuple(
            Thread(target=lambda index, element_id: results.__setitem__(
                index, self.load(element_id)),
                   args=(index, element_id)) for index, element_id in enumerate(element_ids))
        tuple(map(Thread.start, threads))
        tuple(map(Thread.join, threads))
        return results

    def load_all(self) -> Iterable[T]:
        docs = self.collection.find()
        return map(self.conv_to_dbclass, docs)

    def update(self, element: T) -> T:
        all_fields = element.serialize()
        _id = all_fields.pop("_id")
        self.collection.update_one({"_id": _id}, {"$set": all_fields})
        return element

    def write(self, element: T) -> T:
        self.collection.insert_one(element.serialize())
        return element

    def write_multiple(self, elements: Sequence[T]) -> list[T]:
        results = [T for _ in elements]
        threads = tuple(
            Thread(target=lambda index, element_id: results.__setitem__(
                index, self.write(element)),
                   args=(index, element)) for index, element in enumerate(elements))
        tuple(map(Thread.start, threads))
        tuple(map(Thread.join, threads))
        return results

    def conv_to_dbclass(self, doc) -> T:
        dict_repr = dict(doc)
        element = self.operated_class.deserialize(dict_repr)
        return element

    def export_csv(self, path: Path) -> None:
        if not path.name.endswith('.csv'):
            raise ValueError(f'{path=} must be a csv file.')
        file = path.open('w')
        header = None
        for entity in self.load_all():
            serialized = entity.serialize()
            if header is None:
                header = serialized.keys()
                file.write(','.join(header))
            file.write(','.join(serialized[column] for column in header))
        file.close()

    def load_from_csv(self, path: Path) -> None:
        if not path.name.endswith('.csv'):
            raise ValueError(f'{path=} must be a csv file.')
        file = path.open()
        csv_reader = csv.DictReader(file)
        threads = []
        for row in csv_reader:
            serialized = self.operated_class.deserialize(row)
            threads.append(Thread(target=self.write(serialized)))
            threads[-1].start()
        file.close()
        for thread in threads:
            thread.join()


class NoSuchElementException(ValueError):
    pass
