import werkzeug.exceptions
from flask_jwt_extended import create_access_token
from flask_pydantic import validate
from flask_restful import Resource

from src.constants.account_model_constants import AccountModelConstants
from src.models import LoginModel, AccountModel
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
                identity=user_from_db[AccountModelConstants.USERNAME],
                additional_claims={
                    AccountModelConstants.FIRST_NAME: user_from_db[AccountModelConstants.FIRST_NAME],
                    AccountModelConstants.LAST_NAME: user_from_db[AccountModelConstants.LAST_NAME],
                    AccountModelConstants.ROL: user_from_db[AccountModelConstants.ROL]
                }
            )

            print('llego')
            return make_api_http_response(
                status=200,
                message="Success Authentication",
                data={"access_token": access_token},
            ), 200

        return self.__get_user_or_password_incorrect_response(), werkzeug.exceptions.Unauthorized.code

    @staticmethod
    def __get_user_or_password_incorrect_response():
        return make_api_http_response(
            status=werkzeug.exceptions.Unauthorized.code,
            message="The username or password is incorrect",
            error=True
        )
