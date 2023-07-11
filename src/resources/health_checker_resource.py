from flask_restful import Resource

from src.utils.api_http_response_helper import make_api_http_response


class HealthCheckerResource(Resource):
    def get(self):
        return make_api_http_response(
                status=200,
                message="Hello, I am alive"
            ),  200
