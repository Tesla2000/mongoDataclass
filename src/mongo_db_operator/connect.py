from pymongo import MongoClient
from pymongo.database import Database


def connect(
    database_name: str,
    host: str = "localhost",
    username: str = None,
    password: str = None,
    port=27017,
) -> Database:
    if username and password:
        connection_string = (
            f"mongodb://{username}:{password}@{host}:{port}"
        )
    else:
        connection_string = f"mongodb://{host}:{port}"
    client = MongoClient(connection_string)
    return client[database_name]
