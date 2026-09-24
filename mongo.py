from pymongo import MongoClient

from config import MONGO_URI, DATABASE_NAME

cliente = MongoClient(MONGO_URI, serverSelectionTimeoutMS=10000)
db = cliente[DATABASE_NAME]

# Colecciones
usuarios = db.usuarios
