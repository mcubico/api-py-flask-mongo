import werkzeug.exceptions
from flask import jsonify
from flask_jwt_extended import create_access_token, set_access_cookies
from flask_pydantic import validate
from flask_restful import Resource

from src.constants.account_model_constants import AccountModelConstants
from src.constants.message_constants import MessageConstants
from src.models import LoginModel
from src.utils.api_http_response_helper import make_api_http_response
from src.utils.encrypt_helper import encrypt_password
from src.utils.user_db_helper import UserDbHelper


class LoginResource(Resource):
    @validate()
    def post(self, body: LoginModel):
        user_from_db = UserDbHelper().find_user_by_username(body.username)
        if not user_from_db:
            return self.__get_user_or_password_incorrect_response(), werkzeug.exceptions.Unauthorized.code

        # Check if password is correct
        encrypted_password = encrypt_password(body.password)
        if encrypted_password == user_from_db[AccountModelConstants.PASSWORD]:
            access_token = create_access_token(
                identity=user_from_db[AccountModelConstants.USERNAME]
            )
            response = make_api_http_response(
                status=200,
                message=MessageConstants.SUCCESSFUL_AUTHENTICATION,
                data={"access_token": access_token},
            )
            set_access_cookies(jsonify(response), access_token)

            return response

        return self.__get_user_or_password_incorrect_response(), werkzeug.exceptions.Unauthorized.code

    @staticmethod
    def __get_user_or_password_incorrect_response():
        return make_api_http_response(
            status=werkzeug.exceptions.Unauthorized.code,
            message=MessageConstants.USER_OR_PASSWORD_INCORRECT,
            error=True
        )
