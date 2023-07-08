import datetime
import hashlib
import os
import pymongo
import werkzeug.exceptions

from . import app
from flask import jsonify, request, make_response
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_pydantic import validate
from markupsafe import escape
from pydantic import ValidationError
from pymongo.errors import DuplicateKeyError
from .models import LoginModel, PaginationModel, OrderPaginationEnum, RiskModel
from .db import get_db_client


def handle_error(error):
    return {'error': str(error)}, werkzeug.exceptions.InternalServerError.code


app.register_error_handler(Exception, handle_error)

database = os.getenv("MONGO_DB_DATABASE")

client = get_db_client()
db = client[database]

risks_collection = db["Risks"]
risks_collection.create_index("risk")
risks_collection.create_index("description")

features_collection = db["Features"]

users_collection = db["Users"]
users_collection.create_index("username")

# initialize JWTManager
jwt = JWTManager(app)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
# define the life span of the token
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = datetime.timedelta(days=1)


@app.route("/api/v1/health-checker", methods=["GET"])
def health_checker():
    return jsonify({"msg": "Hello, I am alive"}), 200


@app.route("/api/v1/login", methods=["POST"])
@validate()
def login(body: LoginModel):
    try:
        user_from_db = get_user_by_username(body.username)
        if not user_from_db:
            return {"error": "The username or password is incorrect"}, 401

        # Check if password is correct
        encrypted_password = encrypt_password(body.password)
        if encrypted_password == user_from_db["password"]:
            # Create JWT Access Token
            access_token = create_access_token(
                identity=user_from_db["username"]
            )  # create jwt token
            # Return Token
            return jsonify(access_token=access_token), 200

        return {"error": "The username or password is incorrect"}, 401
    except Exception as e:
        app.logger.error(e)
        return {"error": "Unexpected error"}, 500


@app.route("/api/v1/users", methods=["POST"])
@jwt_required()
def register_user():
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return {"error": "Access Token Expired"}, 404

        # store the json body request
        payload = request.get_json()

        # Creating Hash of password and encrypt it to store in the database
        payload["password"] = encrypt_password(payload["password"])

        # If not exists than create one
        if user_exists(payload["username"]):
            return {"error": "Username already exists"}, 409

        # Creating user
        _ = users_collection.insert_one(payload)
        return {"msg": "User created successfully"}, 201
    except Exception as e:
        app.logger.error(e)
        return {"error": "Unexpected error"}, 500


@app.route("/api/v1/risks", methods=["POST"])
@jwt_required()
@validate()
def create_risk(body: RiskModel):
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return {"error": "Access Token Expired"}, 404

        # Viewing if risk already present in collection
        body.risk = body.risk.lower()
        risk_from_db = risks_collection.find_one({"risk": body.risk})
        if risk_from_db:
            return jsonify({"error": "Risk already exists on your profile"}), 404

        with client.start_session() as transaction:

            def cb(transaction):
                risk_id = risks_collection.insert_one(
                    {"risk": body.risk, "description": body.description, "active": True}
                ).inserted_id

                features_collection.insert_one(
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
    except Exception as e:
        app.logger.error(e)
        return {"error": "Unexpected error"}, 500


@app.route("/api/v1/risks/<int:risk_id>", methods=["PUT"])
@jwt_required()
def update_risk(risk_id: int):
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return jsonify({"error": "Access Token Expired"}), 404

        # Getting the risk details from json
        payload = request.args
        result = risks_collection.find_one_and_update(
            {"_id": risk_id}, {"$set", {"active": payload["active"]}}
        )

        return jsonify({"msg": "Risk updated successfully", "data": result}), 200
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": "Unexpected error"}), 500


@app.route("/api/v1/risks", methods=["GET"])
@jwt_required()
def fetch_risks():
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return {"error": "Access Token Expired"}, 404

        query_parameters = request.args
        pagination = PaginationModel(**query_parameters)
        risks = list(
            risks_collection.aggregate(pipeline=get_query_to_fetch_risks(pagination))
        )

        response = make_response({"data": risks}, 200)
        response.headers["x-total-count"] = risks[0]["count"]

        return response
    except Exception as e:
        app.logger.error(e)
        return {"error": "Unexpected error"}, 500


def user_exists(username):
    doc = get_user_by_username(username)
    return doc is not None


def get_user_by_username(username):
    return users_collection.find_one({"username": escape(username)})


def encrypt_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_query_to_fetch_risks(pagination: PaginationModel):
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
        {"$unset": ["_id", "active", "features._id"]},
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


@app.errorhandler(werkzeug.exceptions.NotFound)
def handle_not_found_error(e):
    response = {
        'error': f'route: {request.path} not found on this server'
    }
    return response, werkzeug.exceptions.NotFound.code


@app.errorhandler(DuplicateKeyError)
def duplicate_key_error_mongo(e):
    response = {'error': 'Duplicate key error'}
    return response, werkzeug.exceptions.BadRequest.code


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_internal_server_error(e):
    app.logger.error(e)
    return {'error': 'Unexpected error.'}, werkzeug.exceptions.InternalServerError.code


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def handle_method_not_allowed(e):
    app.logger.error(e)
    return {'error': 'Method not allowed.'}, werkzeug.exceptions.InternalServerError.code


@app.errorhandler(ValidationError)
def handle_pydantic_validation_errors(e):
    return jsonify(error=e.errors()), werkzeug.exceptions.BadRequest.code
