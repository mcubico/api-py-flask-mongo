from flask_jwt_extended import create_access_token
from flask_pydantic import validate
from flask_restful import Resource

from src.models import LoginModel
from src.utils.encrypt_helper import encrypt_password
from src.utils.user_db_helper import UserDbHelper


class LoginResource(Resource):
    @validate()
    def post(self, body: LoginModel):
        user_from_db = UserDbHelper().find_user_by_username(body.username)
        if not user_from_db:
            return {"error": "The username or password is incorrect"}, 401

        # Check if password is correct
        encrypted_password = encrypt_password(body.password)
        if encrypted_password == user_from_db["password"]:
            # Create JWT Access Token
            access_token = create_access_token(
                identity=user_from_db["username"]
            )

            return {'access_token': access_token}, 200

        return {"error": "The username or password is incorrect"}, 401
