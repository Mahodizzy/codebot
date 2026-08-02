from config import ADMIN_ID


def es_admin(user_id):
    return user_id == ADMIN_ID


def obtener_permisos(user_id):

    if es_admin(user_id):
        return ["*"]

    usuario = usuarios.find_one(
        {"user_id": str(user_id)}
    )

    if usuario:
        return usuario.get("permisos", [])

    return []


def tiene_permiso(user_id, permiso):

    permisos = obtener_permisos(user_id)

    if not permisos:
        return False, "Usuario sin permisos"

    if "*" in permisos:
        return True, "Administrador"

    if permiso in permisos:
        return True, "Permiso concedido"

    return False, "No tienes permiso para usar este servicio"
