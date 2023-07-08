from flask_restful import Resource


class HealthCheckerResource(Resource):
    def get(self):
        return {"message": "Hello, I am alive"}
