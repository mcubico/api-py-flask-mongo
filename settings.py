from os import environ

FLASK_ENV = environ.get('FLASK_ENV')
FLASK_APP = environ.get('FLASK_APP')
FLASK_RUN_PORT = environ.get('FLASK_RUN_PORT')
FLASK_RUN_HOST = environ.get('FLASK_RUN_HOST')

MONGO_DB_PROTOCOL = environ.get('MONGO_DB_PROTOCOL')
MONGO_DB_CLUSTER = environ.get('MONGO_DB_CLUSTER')
MONGO_DB_HOST = environ.get('MONGO_DB_HOST')
MONGO_DB_USERNAME = environ.get('MONGO_DB_USERNAME')
MONGO_DB_PASSWORD = environ.get('MONGO_DB_PASSWORD')
MONGO_DB_DATABASE = environ.get('MONGO_DB_DATABASE')

JWT_SECRET_KEY = environ.get('JWT_SECRET_KEY')
