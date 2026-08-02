from config import ADMIN_ID
from services.database.mongo import usuarios


def es_admin(user_id):
    """
    Verifica si el usuario es administrador.
    """
    return user_id == ADMIN_ID



def obtener_usuario(user_id):
    """
    Busca un usuario registrado en MongoDB.
    """

    return usuarios.find_one(
        {
            "user_id": str(user_id)
        }
    )



def obtener_correos_autorizados(user_id):
    """
    Devuelve la lista de correos permitidos
    para un usuario.
    """

    # El administrador tiene acceso total
    if es_admin(user_id):
        return ["*"]


    usuario = obtener_usuario(user_id)


    if not usuario:
        return []


    return usuario.get(
        "correos",
        []
    )



def tiene_permiso(user_id, correo):
    """
    Verifica si el usuario puede consultar
    ese correo específico.
    """

    correos = obtener_correos_autorizados(
        user_id
    )


    # Administrador
    if "*" in correos:
        return True, "Administrador"


    correo = correo.lower().strip()


    if correo in correos:
        return True, "Correo autorizado"


    return False, (
        "❌ No tienes permiso para consultar "
        "este correo."
    )
