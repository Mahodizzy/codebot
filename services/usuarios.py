from services.database.mongo import usuarios


def registrar_usuario(
    user_id,
    cuentas=None
):
    """
    Crea un usuario nuevo.
    """

    usuario = {
        "user_id": str(user_id),
        "cuentas": cuentas or []
    }

    usuarios.insert_one(
        usuario
    )

    return True



def buscar_usuario(
    user_id
):
    """
    Busca un usuario por Telegram ID.
    """

    return usuarios.find_one(
        {
            "user_id": str(user_id)
        }
    )



def listar_usuarios():
    """
    Devuelve todos los usuarios.
    """

    return list(
        usuarios.find()
    )



def eliminar_usuario(
    user_id
):
    """
    Elimina un usuario.
    """

    resultado = usuarios.delete_one(
        {
            "user_id": str(user_id)
        }
    )

    return resultado.deleted_count > 0



def agregar_cuenta(
    user_id,
    servicio,
    correo
):
    """
    Agrega un correo autorizado.
    """

    usuarios.update_one(

        {
            "user_id": str(user_id)
        },

        {
            "$push": {
                "cuentas": {
                    "servicio": servicio,
                    "correo": correo
                }
            }
        }

    )

    return True
