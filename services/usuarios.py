from services.database.mongo import usuarios


def registrar_usuario(user_id, correo):
    """
    Crea un usuario nuevo
    con su primer correo autorizado.
    """

    usuario_existente = usuarios.find_one(
        {
            "user_id": str(user_id)
        }
    )

    if usuario_existente:

        return agregar_correo(
            user_id,
            correo
        )


    usuarios.insert_one(
        {
            "user_id": str(user_id),
            "correos": [
                correo.lower().strip()
            ]
        }
    )

    return True



def agregar_correo(user_id, correo):
    """
    Agrega un correo autorizado
    a un usuario existente.
    """

    correo = correo.lower().strip()


    usuario = usuarios.find_one(
        {
            "user_id": str(user_id)
        }
    )


    if not usuario:

        return False



    correos = usuario.get(
        "correos",
        []
    )


    if correo in correos:

        return False



    correos.append(
        correo
    )


    usuarios.update_one(

        {
            "user_id": str(user_id)
        },

        {
            "$set": {
                "correos": correos
            }
        }

    )


    return True



def obtener_usuario(user_id):
    """
    Busca un usuario.
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



def eliminar_usuario(user_id):
    """
    Elimina completamente un usuario.
    """

    resultado = usuarios.delete_one(
        {
            "user_id": str(user_id)
        }
    )


    return resultado.deleted_count > 0



def eliminar_correo(user_id, correo):
    """
    Elimina un correo específico
    sin borrar al usuario.
    """

    usuario = obtener_usuario(
        user_id
    )


    if not usuario:

        return False



    correos = usuario.get(
        "correos",
        []
    )


    correo = correo.lower().strip()



    if correo not in correos:

        return False



    correos.remove(
        correo
    )



    usuarios.update_one(

        {
            "user_id": str(user_id)
        },

        {
            "$set": {
                "correos": correos
            }
        }

    )


    return True
