import pymongo
import datetime
import hashlib

import werkzeug.exceptions
from bson import ObjectId
from flask import Flask, request, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
from flask_pydantic import validate, ValidationError
from pymongo import MongoClient
from urllib.parse import quote_plus
from markupsafe import escape
from pymongo.errors import DuplicateKeyError

from models import LoginModel, PaginationModel, OrderPaginationEnum, RiskModel

app = Flask(__name__)

# Initialize connection to db
protocol = 'mongodb+srv'
username = quote_plus('mcubico')
password = quote_plus('iWqfcqc7QJHRAMqD')
cluster = 'clustercybersecurityris'
hostname = 'yx2qthd.mongodb.net'
database = 'CyberSecurityRisks'
uri = f'{protocol}://{username}:{password}@{cluster}.{hostname}/{database}?retryWrites=true&w=majority'

client = MongoClient(uri)

db = client[database]

risks_collection = db['Risks']
risks_collection.create_index('risk')
risks_collection.create_index('description')

features_collection = db['Features']

users_collection = db['Users']
users_collection.create_index('username')

# initialize JWTManager
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = '9da06b778ddf921de7358a56b3b59ebc'
# define the life span of the token
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=1)


@app.route('/api/v1/ping')
def ping():
    return jsonify({'msg': 'Hello, I am alive'}), 200


@app.route("/api/v1/users", methods=["POST"])
@jwt_required()
def register():
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return jsonify({'error': 'Access Token Expired'}), 404

        # store the json body request
        payload = request.get_json()

        # Creating Hash of password and encrypt it to store in the database
        payload["password"] = encrypt_password(payload['password'])

        # If not exists than create one
        if user_exists(payload["username"]):
            return jsonify({'error': 'Username already exists'}), 409

        # Creating user
        _ = users_collection.insert_one(payload)
        return jsonify({'msg': 'User created successfully'}), 201
    except Exception as e:
        app.logger.error(e)
        return jsonify({'error': 'Unexpected error'}), 500


@app.route("/api/v1/login", methods=["POST"])
@validate()
def login(body: LoginModel):
    try:
        user_from_db = get_user_by_username(body.username)
        if not user_from_db:
            return jsonify({'error': 'The username or password is incorrect'}), 401

        # Check if password is correct
        encrypted_password = encrypt_password(body.password)
        if encrypted_password == user_from_db['password']:
            # Create JWT Access Token
            access_token = create_access_token(identity=user_from_db['username'])  # create jwt token
            # Return Token
            return jsonify(access_token=access_token), 200

        return jsonify({'error': 'The username or password is incorrect'}), 401
    except Exception as e:
        app.logger.error(e)
        return jsonify({'error': 'Unexpected error'}), 500


@app.route("/api/v1/risks", methods=["POST"])
@jwt_required()
@validate()
def create_risk(body: RiskModel):
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return jsonify({'error': 'Access Token Expired'}), 404

        # Viewing if risk already present in collection
        body.risk = body.risk.lower()
        risk_from_db = risks_collection.find_one({'risk': body.risk})
        if risk_from_db:
            return jsonify({'error': 'Risk already exists on your profile'}), 404

        with client.start_session() as transaction:
            def cb(transaction):
                risk_id = risks_collection.insert_one({
                    'risk': body.risk,
                    'description': body.description,
                    'active': True
                }).inserted_id

                features_collection.insert_one({
                    '_id': risk_id,
                    'vulnerability': body.features.vulnerability,
                    'probability': body.features.probability,
                    'impact': body.features.impact,
                    'thread': body.features.thread,
                })

            transaction.with_transaction(cb)

        return jsonify({'msg': 'Risk created successfully'}), 201
    except Exception as e:
        app.logger.error(e)
        return jsonify({'error': 'Unexpected error'}), 500


@app.route("/api/v1/risks/<int:risk_id>", methods=["PUT"])
@jwt_required()
def update_risk(risk_id: int):
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return jsonify({'error': 'Access Token Expired'}), 404

        # Getting the risk details from json
        payload = request.args
        result = risks_collection.find_one_and_update({'_id': risk_id}, {'$set', {'active': payload['active']}})

        return jsonify({'msg': 'Risk updated successfully', 'data': result}), 200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'error': 'Unexpected error'}), 500


@app.route('/api/v1/risks', methods=['GET'])
@jwt_required()
def fetch_risks():
    try:
        # Getting the user from access token
        username_from_jwt = get_jwt_identity()
        user_from_db = get_user_by_username(username_from_jwt)

        if not user_from_db:
            return jsonify({'error': 'Access Token Expired'}), 404

        query_parameters = request.args
        pagination = PaginationModel(**query_parameters)
        risks = list(
            risks_collection.aggregate(
                pipeline=get_query_to_fetch_risks(pagination)
            )
        )

        response = make_response(jsonify({"data": risks}), 200)
        response.headers['x-total-count'] = risks[0]['count']

        return response
    except Exception as e:
        app.logger.error(e)
        return jsonify({'error': 'Unexpected error'}), 500


@app.errorhandler(404)
def resource_not_found(e):
    """
    An error-handler to ensure that 404 errors are returned as JSON.
    """
    return jsonify(error=str(e)), 404


@app.errorhandler(DuplicateKeyError)
def resource_not_found(e):
    return jsonify(error=f"Duplicate key error."), 400


@app.errorhandler(werkzeug.exceptions.InternalServerError)
def handle_exception(e):
    app.logger.error(e)
    return jsonify(error=f"Unexpected error."), 500


@app.errorhandler(werkzeug.exceptions.MethodNotAllowed)
def handle_exception(e):
    app.logger.error(e)
    return jsonify(error=f"Method not allowed."), 405


@app.errorhandler(ValidationError)
def handle_pydantic_validation_errors(e):
    return jsonify(e.errors())


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
            '$lookup': {
                'from': 'Features',
                'localField': '_id',
                'foreignField': '_id',
                'as': 'features'
            }
        },
        {'$addFields': {'risks._id': {'$toString': '$_id'}}},
        {'$unset': ['_id', 'active', 'features._id']}
    ]

    if pagination.query:
        query_escaped = escape(pagination.query)
        query.append({
            '$match': {
                '$or': [
                    {'risks._id': {'$regex': query_escaped}},
                    {'risk': {'$regex': query_escaped}},
                    {'description': {'$regex': query_escaped}}
                ]
            }
        })

    direction = pymongo.ASCENDING if pagination.order == OrderPaginationEnum.ASCENDING else pymongo.DESCENDING
    if pagination.order_by:
        query.append({'$sort': {f'features.{pagination.order_by.value}': direction}})

    query.append({
        '$group': {
            '_id': None,
            'count': {'$sum': 1},
            'results': {'$push': '$$ROOT'}
        }
    })

    row_start = pagination.limit * (pagination.page - 1)
    query.append({
        '$project': {
            'count': 1,
            '_id': 0,
            'rows': {'$slice': ['$results', row_start, pagination.limit]},
        }
    })

    return query
