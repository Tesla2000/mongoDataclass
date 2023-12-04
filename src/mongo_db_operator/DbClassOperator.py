from typing import Type, Any, Iterable

from pymongo.database import Database

from seriattrs import DbClass


class DbClassOperator:
    def __init__(self, db: Database, operated_class: Type[DbClass]):
        self.db = db
        if not issubclass(operated_class, DbClass):
            raise ValueError(f"{operated_class=} must be a subclass of DbClass")
        self.operated_class = operated_class
        self.collection_name = operated_class.__name__
        self.collection = self.db[self.collection_name]

    def delete(self, element: DbClass):
        result = self.collection.delete_one({"_id": str(element._id)})
        if result.deleted_count != 1:
            raise NoSuchElementException(f"No {element=} present in the database")
        del element

    def load(self, object_id: Any) -> DbClass:
        document = self.collection.find_one({"_id": str(object_id)})
        if not document:
            raise NoSuchElementException(
                f"No element with _id={object_id} in the collection_name={self.collection_name}"
            )
        return self._conv_to_element(document)

    def load_all(self) -> Iterable[DbClass]:
        docs = self.collection.find()
        return map(self._conv_to_element, docs)

    def update(self, element: DbClass):
        all_fields = element.serialize()
        _id = all_fields.pop("_id")
        result = self.collection.update_one({"_id": _id}, {"$set": all_fields})
        if result.modified_count != 1:
            raise NoSuchElementException(
                f"No element with {_id=} in the collection_name={self.collection_name}"
            )

    def write(self, element: DbClass):
        self.collection.insert_one(element.serialize())
        return element

    def _conv_to_element(self, doc) -> DbClass:
        dict_repr = dict(doc)
        element = self.operated_class.deserialize(dict_repr)
        return element


class NoSuchElementException(ValueError):
    pass
