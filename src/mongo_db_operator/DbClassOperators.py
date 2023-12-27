from typing import Type

from pymongo.database import Database
from seriattrs import DbClass

from .DbClassOperator import DbClassOperator


class DbClassOperators(dict):
    def __init__(self, db: Database, dictionary: dict = None, **kwargs):
        self.db = db
        if dictionary is None:
            dictionary = {}
        super().__init__(dict(**dictionary, **kwargs))

    def __getitem__(self, item: Type[DbClass]) -> DbClassOperator:
        if not issubclass(item, DbClass):
            raise ValueError("Item must be a subclass of DbClass")
        try:
            return super().__getitem__(item)
        except KeyError:
            self[item] = DbClassOperator(self.db, item)
            return self[item]
