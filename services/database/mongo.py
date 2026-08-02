from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME
)


# Conexión MongoDB

cliente = MongoClient(
    MONGO_URI
)


# Base de datos

db = cliente[
    DATABASE_NAME
]


# Colección usuarios

usuarios = db["usuarios"]
