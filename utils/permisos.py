from config import ADMIN_ID

from services.usuarios import (
    usuario_tiene_correo,
    buscar_usuario
)


# ==================================
# ADMIN
# ==================================

def es_admin(user_id):

    return int(user_id) == int(ADMIN_ID)



# ==================================
# OBTENER PERMISOS
# ==================================

def obtener_permisos(user_id):

    if es_admin(user_id):

        return ["*"]


    usuario = buscar_usuario(
        user_id
    )


    if not usuario:

        return []


    return usuario.get(
        "permisos",
        []
    )



# ==================================
# VERIFICAR CORREO
# ==================================

def tiene_permiso_correo(
        user_id,
        correo
):

    # Administrador pasa siempre

    if es_admin(user_id):

        return True, "Administrador"



    permitido = usuario_tiene_correo(
        user_id,
        correo
    )


    if permitido:

        return True, "Correo autorizado"



    return False, "Este correo no está autorizado para tu cuenta."



# ==================================
# VERIFICAR USUARIO EXISTENTE
# ==================================

def usuario_autorizado(user_id):

    if es_admin(user_id):

        return True


    usuario = buscar_usuario(
        user_id
    )


    return usuario is not None