import werkzeug.exceptions
from flask import request, jsonify

from src.utils.api_http_response_helper import make_api_http_response


def handle_error(error):
    return make_api_http_response(
        status=werkzeug.exceptions.InternalServerError.code,
        message='Error: Unexpected error',
        error=True
    ), werkzeug.exceptions.InternalServerError.code


def handle_not_found_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.NotFound.code,
        message=f'Error: Route {request.path} not found on this server',
        error=True
    ), werkzeug.exceptions.NotFound.code


def unauthorized_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.Unauthorized.code,
        message=f'Error: Unauthorized error -> {e}',
        error=True
    ), werkzeug.exceptions.Unauthorized.code


def handle_duplicate_key_mongo_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.BadRequest.code,
        message='Error: Duplicate key error',
        error=True
    ), werkzeug.exceptions.BadRequest.code


def handle_internal_server_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.InternalServerError.code,
        message='Error: Unexpected error.',
        error=True
    ), werkzeug.exceptions.InternalServerError.code


def handle_method_not_allowed_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.MethodNotAllowed.code,
        message='Error: Method not allowed.',
        error=True
    ), werkzeug.exceptions.MethodNotAllowed.code


def handle_pydantic_validation_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.BadRequest.code,
        message='Error: Method not allowed.',
        data=jsonify(error=e.errors()),
        error=True
    ), werkzeug.exceptions.BadRequest.code
