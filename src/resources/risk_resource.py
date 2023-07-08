import pymongo
from flask import request, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_pydantic import validate
from flask_restful import Resource
from markupsafe import escape

from src.models import RiskModel, PaginationModel, OrderPaginationEnum
from src.mongo_database import MongoDataBase
from src.utils.user_db_helper import UserDbHelper


class RiskResource(Resource):
    def __init__(self):
        self._mongo_database = MongoDataBase()
        self._client = self._mongo_database.get_client()
        self._db = self._mongo_database.get_db()

        self._risks_collection = self._db["Risks"]
        self._risks_collection.create_index("risk")
        self._risks_collection.create_index("description")

        self._features_collection = self._db["Features"]

    @jwt_required()
    @validate()
    def post(self, body: RiskModel):
        user_db_helper = UserDbHelper()
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = user_db_helper.find_user_by_username(username_from_jwt)

        if not user_from_db:
            return {"error": "Access Token Expired"}, 404

        # Viewing if risk already present in collection
        body.risk = body.risk.lower()
        risk_from_db = self._risks_collection.find_one({"risk": body.risk})
        if risk_from_db:
            return {"error": "Risk already exists"}, 404

        with self._client.start_session() as transaction:
            def cb(transaction):
                risk_id = self._risks_collection.insert_one(
                    {"risk": body.risk, "description": body.description, "active": True}
                ).inserted_id

                self._features_collection.insert_one(
                    {
                        "_id": risk_id,
                        "vulnerability": body.features.vulnerability,
                        "probability": body.features.probability,
                        "impact": body.features.impact,
                        "thread": body.features.thread,
                    }
                )

            transaction.with_transaction(cb)

        return {"msg": "Risk created successfully"}, 201

    @jwt_required()
    @validate()
    def get(self):
        user_db_helper = UserDbHelper()
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = user_db_helper.find_user_by_username(username_from_jwt)

        if not user_from_db:
            return {"error": "Access Token Expired"}, 404

        query_parameters = request.args
        pagination = PaginationModel(**query_parameters)
        risks = list(
            self._risks_collection.aggregate(pipeline=self.__get_query_to_fetch_risks(pagination=pagination))
        )

        response = make_response({"data": risks}, 200)
        response.headers["x-total-count"] = risks[0]["count"]

        return response

    @staticmethod
    def __get_query_to_fetch_risks(pagination: PaginationModel):
        query = [
            {
                "$lookup": {
                    "from": "Features",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "features",
                }
            },
            {"$addFields": {"risks._id": {"$toString": "$_id"}}},
            {"$unset": ["_id", "features._id"]},
        ]

        if pagination.query:
            query_escaped = escape(pagination.query)
            query.append(
                {
                    "$match": {
                        "$or": [
                            {"risks._id": {"$regex": query_escaped}},
                            {"risk": {"$regex": query_escaped}},
                            {"description": {"$regex": query_escaped}},
                        ]
                    }
                }
            )

        direction = (
            pymongo.ASCENDING
            if pagination.order == OrderPaginationEnum.ASCENDING
            else pymongo.DESCENDING
        )
        if pagination.order_by:
            query.append({"$sort": {f"features.{pagination.order_by.value}": direction}})

        query.append(
            {"$group": {"_id": None, "count": {"$sum": 1}, "results": {"$push": "$$ROOT"}}}
        )

        row_start = pagination.limit * (pagination.page - 1)
        query.append(
            {
                "$project": {
                    "count": 1,
                    "_id": 0,
                    "rows": {"$slice": ["$results", row_start, pagination.limit]},
                }
            }
        )

        return query

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close_db()
