import werkzeug.exceptions
from flask import request, jsonify

from src import application
from src.utils.api_http_response_helper import make_api_http_response


def handle_error(error):
    app.logger.error(str(error))
    return make_api_http_response(
        status=werkzeug.exceptions.InternalServerError.code,
        message='Unexpected error.',
        error=True
    ), werkzeug.exceptions.InternalServerError.code


def handle_not_found_error(e):
    return make_api_http_response(
        status=werkzeug.exceptions.NotFound.code,
        message=f'route: {request.path} not found on this server',
        error=True
    ), werkzeug.exceptions.NotFound.code


def duplicate_key_error_mongo(e):
    return make_api_http_response(
        status=werkzeug.exceptions.BadRequest.code,
        message='Duplicate key error',
        error=True
    ), werkzeug.exceptions.BadRequest.code


def handle_internal_server_error(e):
    app.logger.error(e)
    return make_api_http_response(
        status=werkzeug.exceptions.InternalServerError.code,
        message='Unexpected error.',
        error=True
    ), werkzeug.exceptions.InternalServerError.code


def handle_method_not_allowed(e):
    return make_api_http_response(
        status=werkzeug.exceptions.MethodNotAllowed.code,
        message='Method not allowed.',
        error=True
    ), werkzeug.exceptions.MethodNotAllowed.code


def handle_pydantic_validation_errors(e):
    return make_api_http_response(
        status=werkzeug.exceptions.BadRequest.code,
        message='Method not allowed.',
        data=jsonify(error=e.errors()),
        error=True
    ), werkzeug.exceptions.BadRequest.code
