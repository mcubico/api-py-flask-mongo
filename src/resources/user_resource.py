from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flask_restful import Resource

from src.models import LoginModel
from src.mongo_database import MongoDataBase
from src.utils.encrypt_helper import encrypt_password
from src.utils.user_db_helper import UserDbHelper


class UserResource(Resource):
    def __init__(self):
        self._mongo_database = MongoDataBase()
        self._client = self._mongo_database.get_client()
        self._db = self._mongo_database.get_db()

        self._users_collection = self._db["Users"]
        self._users_collection.create_index("username")

    @jwt_required()
    @validate()
    def post(self, body: LoginModel):
        user_db_helper = UserDbHelper()

        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = user_db_helper.find_user_by_username(username_from_jwt)

        if not user_from_db:
            return {"error": "Access Token Expired"}, 401

        # If not exists than create one
        user_from_db = user_db_helper.find_user_by_username(body.username)
        if user_from_db:
            return {"error": "Username already exists"}, 409

        body.password = encrypt_password(body.password)

        # Creating user
        _ = self._users_collection.insert_one(body.to_json())
        return {"message": "User created successfully"}, 201

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close_db()
