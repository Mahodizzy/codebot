from config import ADMIN_ID
from services.database.mongo import usuarios



def es_admin(user_id):

    return user_id == ADMIN_ID




def obtener_usuario(user_id):

    return usuarios.find_one(
        {
            "user_id": str(user_id)
        }
    )




def tiene_permiso(user_id, correo):


    # Admin tiene acceso total

    if es_admin(user_id):

        return True, "Administrador"



    usuario = obtener_usuario(
        user_id
    )


    if not usuario:

        return False, "Usuario no registrado"



    correos = usuario.get(
        "correos",
        []
    )


    if correo.lower() in [
        c.lower()
        for c in correos
    ]:

        return True, "Correo autorizado"



    return False, "Este correo no está autorizado"
