from flask_restful import Resource


class HealthCheckerResource(Resource):
    def get(self):
        return {
                "status": 200,
                "message": "Hello, I am alive",
                "data": None,
                "error": False
            }, 200
