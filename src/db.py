import os

from urllib.parse import quote_plus
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def get_db_client():

    # Initialize connection to db
    protocol = os.getenv("MONGO_DB_PROTOCOL")
    username = quote_plus(os.getenv("MONGO_DB_USERNAME"))
    password = quote_plus(os.getenv("MONGO_DB_PASSWORD"))
    cluster = os.getenv("MONGO_DB_CLUSTER")
    hostname = os.getenv("MONGO_DB_HOST")
    database = os.getenv("MONGO_DB_DATABASE")
    uri = f"{protocol}://{username}:{password}@{cluster}.{hostname}/{database}?retryWrites=true&w=majority"

    return MongoClient(uri)
