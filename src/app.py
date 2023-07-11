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

from src import app
from src.resources.health_checker_resource import HealthCheckerResource
from src.resources.login_resource import LoginResource
from src.resources.risk_resource import RiskResource
from src.resources.user_resource import UserResource
from src.utils.exception_management import handle_error, handle_not_found_error, duplicate_key_error_mongo, \
    handle_internal_server_error, handle_method_not_allowed, handle_pydantic_validation_errors

# Add Routes
api = Api(app=app, prefix='/api')
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

# Add the resources to the API
api.add_resource(HealthCheckerResource, '/', '/health-checker')
api.add_resource(LoginResource, '/auth/login')
api.add_resource(UserResource, '/users')
api.add_resource(RiskResource, '/risks')

# initialize JWTManager
jwt = JWTManager(api.app)
api.app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
# define the life span of the token
api.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)

# Configure Swagger UI
SWAGGER_URL = '/swagger'
API_URL = f'http://{os.getenv("FLASK_RUN_HOST")}:{os.getenv("FLASK_RUN_PORT")}/swagger.json'
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


if __name__ == '__main__':
    api.app.run(debug=True)
