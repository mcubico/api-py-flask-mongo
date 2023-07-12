import werkzeug.exceptions
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, unset_jwt_cookies
from flask_restful import Resource

from src.constants.message_constants import MessageConstants
from src.utils.api_http_response_helper import make_api_http_response
from src.utils.user_db_helper import UserDbHelper


class LogoutResource(Resource):
    @jwt_required()
    def post(self):
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

        response = make_api_http_response(
            status=200,
            message=MessageConstants.LOGOUT_SUCCESSFUL
        )
        unset_jwt_cookies(jsonify(response))
        return response
