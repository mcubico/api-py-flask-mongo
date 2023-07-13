import werkzeug.exceptions
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required, create_access_token, set_access_cookies
from flask_restful import Resource

from src.constants.account_model_constants import AccountModelConstants
from src.constants.message_constants import MessageConstants
from src.utils.api_http_response_helper import make_api_http_response
from src.utils.user_db_helper import UserDbHelper


class TokenResource(Resource):
    @jwt_required()
    def get(self):
        user_db_helper = UserDbHelper()

        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = user_db_helper.find_user_by_username(username_from_jwt)

        if not user_from_db:
            return make_api_http_response(
                status=werkzeug.exceptions.Unauthorized.code,
                message=MessageConstants.ACCESS_TOKEN_EXPIRED,
                error=True
            ), werkzeug.exceptions.Unauthorized.code

        access_token = create_access_token(
            identity=user_from_db[AccountModelConstants.USERNAME]
        )

        response = make_api_http_response(
            status=200,
            message=MessageConstants.TOKEN_SUCCESSFULLY_REFRESHED,
            data={"access_token": access_token},
        )

        response_json = jsonify(response)
        set_access_cookies(response_json, access_token)

        return response
