from services.database.mongo import usuarios


def registrar_usuario(user_id, permisos):
    """
    Registra un usuario nuevo o actualiza sus permisos.
    """

    usuarios.update_one(
        {"user_id": str(user_id)},
        {
            "$set": {
                "user_id": str(user_id),
                "permisos": permisos
            }
        },
        upsert=True
    )

    return True


def eliminar_usuario(user_id):
    """
    Elimina un usuario.
    """

    resultado = usuarios.delete_one(
        {"user_id": str(user_id)}
    )

    return resultado.deleted_count > 0


def obtener_usuario(user_id):
    """
    Obtiene un usuario.
    """

    return usuarios.find_one(
        {"user_id": str(user_id)}
    )


def listar_usuarios():
    """
    Devuelve todos los usuarios.
    """

    return list(
        usuarios.find()
    )


def actualizar_permisos(user_id, permisos):

    resultado = usuarios.update_one(
        {"user_id": str(user_id)},
        {
            "$set": {
                "permisos": permisos
            }
        }
    )

    return resultado.modified_count > 0
