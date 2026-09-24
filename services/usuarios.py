"""
Usuarios y sus correos autorizados.

Formato de cada documento en Mongo:
    {"user_id": "123456789", "permisos": ["cliente@gmail.com", ...]}

Un permiso "*" da acceso a todos los correos.
"""

import logging

from pymongo.errors import PyMongoError

from services.database.mongo import usuarios

logger = logging.getLogger(__name__)


def _normalizar(correos):
    """Convierte lo que venga (texto o lista) en lista limpia en minúsculas."""
    if not correos:
        return []
    if isinstance(correos, str):
        correos = [correos]
    limpios = []
    for c in correos:
        c = str(c).strip().lower()
        if c and c not in limpios:
            limpios.append(c)
    return limpios


# ==================================
# PREPARAR / REPARAR BASE DE DATOS
# ==================================

def preparar_base_datos():
    """
    Repara los datos guardados por la versión anterior del bot:
    - permisos guardados como texto en vez de lista
    - campo viejo "correos"
    - usuarios duplicados con el mismo ID
    Luego crea un índice único para que no vuelvan a duplicarse.
    Se puede ejecutar todas las veces que sea, no daña nada.
    """
    agrupados = {}

    for doc in usuarios.find():
        uid = str(doc.get("user_id", "")).strip()
        if not uid:
            continue
        grupo = agrupados.setdefault(uid, {"ids": [], "permisos": []})
        grupo["ids"].append(doc["_id"])
        for correo in _normalizar(doc.get("permisos")) + _normalizar(doc.get("correos")):
            if correo not in grupo["permisos"]:
                grupo["permisos"].append(correo)

    for uid, grupo in agrupados.items():
        principal, *sobrantes = grupo["ids"]
        usuarios.update_one(
            {"_id": principal},
            {"$set": {"user_id": uid, "permisos": grupo["permisos"]},
             "$unset": {"correos": ""}},
        )
        if sobrantes:
            usuarios.delete_many({"_id": {"$in": sobrantes}})
            logger.info("Usuario %s: se unieron %d registros duplicados", uid, len(sobrantes))

    try:
        usuarios.create_index("user_id", unique=True)
    except PyMongoError:
        logger.exception("No se pudo crear el índice único de user_id")


# ==================================
# CONSULTAS
# ==================================

def buscar_usuario(user_id):
    return usuarios.find_one({"user_id": str(user_id).strip()})


def listar_usuarios():
    return list(usuarios.find().sort("user_id", 1))


def obtener_correos(user_id):
    usuario = buscar_usuario(user_id)
    if not usuario:
        return []
    return _normalizar(usuario.get("permisos"))


def usuario_tiene_correo(user_id, correo):
    permisos = obtener_correos(user_id)
    if "*" in permisos:
        return True
    return correo.strip().lower() in permisos


# ==================================
# MODIFICACIONES
# ==================================

def registrar_usuario(user_id, correos):
    """
    Crea el usuario si no existe y AGREGA los correos
    (no borra los que ya tenía). Devuelve la lista final.
    """
    user_id = str(user_id).strip()
    usuarios.update_one(
        {"user_id": user_id},
        {"$addToSet": {"permisos": {"$each": _normalizar(correos)}}},
        upsert=True,
    )
    return obtener_correos(user_id)


def quitar_correo(user_id, correo):
    """Quita un correo. Devuelve True si el usuario lo tenía."""
    resultado = usuarios.update_one(
        {"user_id": str(user_id).strip()},
        {"$pull": {"permisos": correo.strip().lower()}},
    )
    return resultado.modified_count > 0


def eliminar_usuario(user_id):
    """Elimina al usuario completo. Devuelve True si existía."""
    resultado = usuarios.delete_one({"user_id": str(user_id).strip()})
    return resultado.deleted_count > 0
