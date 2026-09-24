from config import ADMIN_IDS
from services.usuarios import usuario_tiene_correo


def es_admin(user_id):
    try:
        return int(user_id) in ADMIN_IDS
    except (TypeError, ValueError):
        return False


def tiene_permiso_correo(user_id, correo):
    """Devuelve (autorizado, mensaje)."""
    if es_admin(user_id):
        return True, "Administrador"
    if usuario_tiene_correo(user_id, correo):
        return True, "Correo autorizado"
    return False, "🚫 Este correo no está autorizado para tu cuenta."
