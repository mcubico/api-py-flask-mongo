from markupsafe import escape

from src.mongo_database import MongoDataBase


class UserDbHelper:
    def __init__(self):
        self._mongo_database = MongoDataBase()
        self._client = self._mongo_database.get_client()
        self._db = self._mongo_database.get_db()
        self._users_collection = self._db["Users"]

    def find_user_by_username(self, username: str):
        """ Find an user by their username
        :param username: username
        """
        response = self._users_collection.find_one({"username": escape(username)})

        return response

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close_db()
