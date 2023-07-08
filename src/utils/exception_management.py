import werkzeug.exceptions
from flask import request, jsonify

from src import app


def handle_error(error):
    return {'error': str(error)}, werkzeug.exceptions.InternalServerError.code


def handle_not_found_error(e):
    response = {
        'error': f'route: {request.path} not found on this server'
    }

    return response, werkzeug.exceptions.NotFound.code


def duplicate_key_error_mongo(e):
    response = {'error': 'Duplicate key error'}
    return response, werkzeug.exceptions.BadRequest.code


def handle_internal_server_error(e):
    app.logger.error(e)
    return {'error': 'Unexpected error.'}, werkzeug.exceptions.InternalServerError.code


def handle_method_not_allowed(e):
    app.logger.error(e)
    return {'error': 'Method not allowed.'}, werkzeug.exceptions.InternalServerError.code


def handle_pydantic_validation_errors(e):
    return jsonify(error=e.errors()), werkzeug.exceptions.BadRequest.code
