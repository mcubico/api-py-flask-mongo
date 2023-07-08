import os

from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient


class MongoDataBase:
    def __init__(self):
        load_dotenv()
        self._database = os.getenv("MONGO_DB_DATABASE")

        # Initialize connection to db
        protocol = os.getenv("MONGO_DB_PROTOCOL")
        username = quote_plus(os.getenv("MONGO_DB_USERNAME"))
        password = quote_plus(os.getenv("MONGO_DB_PASSWORD"))
        cluster = os.getenv("MONGO_DB_CLUSTER")
        hostname = os.getenv("MONGO_DB_HOST")
        uri = f"{protocol}://{username}:{password}@{cluster}.{hostname}/{self._database}?retryWrites=true&w=majority"

        self._client = MongoClient(uri)
        self._db = self._client[self._database]

    def get_client(self) -> MongoClient:
        return self._client

    def get_db(self):
        return self._db

    def close_db(self) -> None:
        self._client.close()

    # TO CLOSE DB AT THE END!
    def init_app(self):
        self.close_db()
