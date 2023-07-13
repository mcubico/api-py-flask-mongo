import json
import os
import werkzeug.exceptions

from datetime import datetime
from datetime import timedelta
from datetime import timezone
from flask import jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, get_jwt, create_access_token, get_jwt_identity, set_access_cookies
from flask_restful import Api
from flask_swagger_ui import get_swaggerui_blueprint
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError

from src import create_app
from src.resources.health_checker_resource import HealthCheckerResource
from src.resources.login_resource import LoginResource
from src.resources.logout_resource import LogoutResource
from src.resources.risk_resource import RiskResource
from src.resources.token_resource import TokenResource
from src.resources.user_resource import UserResource
from src.utils.exception_management import (
    handle_error, handle_not_found_error, handle_duplicate_key_mongo_error,
    handle_internal_server_error, handle_method_not_allowed_error, handle_pydantic_validation_error, unauthorized_error
)

app = create_app()
api = Api(app=app, prefix='/api')
is_production_env = os.environ.get('FLASK_ENV') == 'production'

# initialize JWTManager
api.app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
api.app.config['JWT_ACCESS_COOKIE_PATH'] = '/api/'
api.app.config['JWT_REFRESH_COOKIE_PATH'] = '/token/refresh'
api.app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY")
api.app.config["JWT_COOKIE_SECURE"] = is_production_env
app.config['JWT_COOKIE_CSRF_PROTECT'] = is_production_env
api.app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)
jwt = JWTManager(api.app)

# Register API errors handler
if is_production_env:
    api.app.register_error_handler(Exception, handle_error)

api.app.register_error_handler(werkzeug.exceptions.NotFound, handle_not_found_error)
api.app.register_error_handler(werkzeug.exceptions.InternalServerError, handle_internal_server_error)
api.app.register_error_handler(werkzeug.exceptions.MethodNotAllowed, handle_method_not_allowed_error)
api.app.register_error_handler(werkzeug.exceptions.Unauthorized, unauthorized_error)
api.app.register_error_handler(DuplicateKeyError, handle_duplicate_key_mongo_error)
api.app.register_error_handler(ValidationError, handle_pydantic_validation_error)

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
api.add_resource(TokenResource, '/token/refresh')
api.add_resource(UserResource, '/users', '/users/me')
api.add_resource(RiskResource, '/risks')

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


# If true this will only allow the cookies that contain your JWTs to be sent
# over https. In production, this should always be set to True
@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))

        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)

        print(f'Token refreshed: {target_timestamp > exp_timestamp}')
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response
