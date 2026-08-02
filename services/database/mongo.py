from pymongo import MongoClient

from config import (
    MONGO_URI,
    DATABASE_NAME
)


# ==========================
# CONEXIÓN MONGO
# ==========================

cliente = MongoClient(
    MONGO_URI
)


# Base de datos del bot

db = cliente[
    DATABASE_NAME
]


# ==========================
# COLECCIONES
# ==========================


usuarios = db.usuarios


cuentas = db.cuentas
