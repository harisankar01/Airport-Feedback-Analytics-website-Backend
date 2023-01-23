import environ
from pymongo import MongoClient
from pymongo.server_api import ServerApi


def connect():
    env = environ.Env()
    # reading .env file
    environ.Env.read_env()
    client = MongoClient(
        env("DB_URL"),
        server_api=ServerApi('1'),
        serverSelectionTimeoutMS=5000
    )
    return client
