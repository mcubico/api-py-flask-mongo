import datetime
import json
import os

import werkzeug.exceptions
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from src import create_app
from src.resources.health_checker_resource import HealthCheckerResource
from src.resources.login_resource import LoginResource
from src.resources.logout_resource import LogoutResource
from src.resources.risk_resource import RiskResource
from src.resources.user_resource import UserResource
from src.utils.exception_management import handle_error, handle_not_found_error, duplicate_key_error_mongo, \
    handle_internal_server_error, handle_method_not_allowed, handle_pydantic_validation_errors

app = create_app()
api = Api(app=app, prefix='/api')

# Register API errors handler
api.app.register_error_handler(Exception, handle_error)
api.app.register_error_handler(werkzeug.exceptions.NotFound, handle_not_found_error)
api.app.register_error_handler(werkzeug.exceptions.InternalServerError, handle_internal_server_error)
api.app.register_error_handler(werkzeug.exceptions.MethodNotAllowed, handle_method_not_allowed)
api.app.register_error_handler(DuplicateKeyError, duplicate_key_error_mongo)
api.app.register_error_handler(ValidationError, handle_pydantic_validation_errors)

# Add CORS
CORS(
    api.app,
    resources={
        r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"], "supports_credentials": True}
    })

# Add API routes
api.add_resource(HealthCheckerResource, '/', '/health-checker')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(LogoutResource, '/auth/logout')
api.add_resource(UserResource, '/users', '/users/me')
api.add_resource(RiskResource, '/risks')

# initialize JWTManager
api.app.config["JWT_TOKEN_LOCATION"] = ["headers", "cookies"]
api.app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
api.app.config["JWT_COOKIE_SECURE"] = True
api.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(hours=1)
jwt = JWTManager(api.app)

# Configure Swagger UI
SWAGGER_URL = '/swagger'
API_URL = f'http://{os.environ.get("FLASK_RUN_HOST")}:{os.environ.get("FLASK_RUN_PORT")}/swagger.json'
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Cyber Security Risks API"
    }
)
api.app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))
