from pymongo import MongoClient
from pymongo.database import Database


def db_connector(
    database_name: str,
    host: str = "localhost",
    username: str = None,
    password: str = None,
    port=27017,
    create_if_not_exist=True,
) -> Database:
    if username and password:
        connection_string = (
            f"mongodb://{username}:{password}@{host}:{port}/{database_name}"
        )
    else:
        connection_string = f"mongodb://{host}:{port}/{database_name}"
    client = MongoClient(connection_string)
    db = client[database_name]
    if create_if_not_exist and database_name not in client.list_database_names():
        print(f"Creating database: {database_name}")
        client.admin.command("create", database_name)

    return db
