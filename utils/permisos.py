from config import ADMIN_ID
from services.database.mongo import usuarios


def es_admin(user_id):
    """
    Devuelve True si el usuario es el administrador.
    """
    return user_id == ADMIN_ID


def obtener_permisos(user_id):
    """
    Obtiene los permisos de un usuario desde MongoDB.
    """

    if es_admin(user_id):
        return ["*"]

    usuario = usuarios.find_one(
        {"user_id": str(user_id)}
    )

    if not usuario:
        return []

    return usuario.get("permisos", [])


def tiene_permiso(user_id, servicio):
    """
    Verifica si el usuario tiene permiso
    para usar un servicio.
    """

    permisos = obtener_permisos(user_id)

    if "*" in permisos:
        return True, "Administrador"

    if servicio in permisos:
        return True, "Acceso permitido"

    return False, f"No tienes permiso para usar {servicio}."
