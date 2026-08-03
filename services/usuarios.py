from services.database.mongo import usuarios


# ==================================
# REGISTRAR USUARIO
# ==================================

def registrar_usuario(user_id, permisos=None):

    usuario = {

        "user_id": str(user_id),

        "permisos": permisos or []

    }


    usuarios.insert_one(usuario)

    return True



# ==================================
# BUSCAR USUARIO
# ==================================

def buscar_usuario(user_id):

    return usuarios.find_one(

        {
            "user_id": str(user_id)
        }

    )



# ==================================
# LISTAR USUARIOS
# ==================================

def listar_usuarios():

    return list(
        usuarios.find()
    )



# ==================================
# ELIMINAR USUARIO
# ==================================

def eliminar_usuario(user_id):

    resultado = usuarios.delete_one(

        {
            "user_id": str(user_id)
        }

    )


    return resultado.deleted_count > 0



# ==================================
# AGREGAR CORREO AUTORIZADO
# ==================================

def agregar_correo(user_id, correo):

    usuarios.update_one(

        {
            "user_id": str(user_id)
        },

        {

            "$push": {

                "permisos": correo

            }

        }

    )


    return True



# ==================================
# QUITAR CORREO AUTORIZADO
# ==================================

def quitar_correo(user_id, correo):

    usuarios.update_one(

        {
            "user_id": str(user_id)
        },

        {

            "$pull": {

                "permisos": correo

            }

        }

    )


    return True



# ==================================
# VERIFICAR CORREO
# ==================================

def usuario_tiene_correo(user_id, correo):

    usuario = buscar_usuario(user_id)


    if not usuario:
        return False


    permisos = usuario.get(
        "permisos",
        []
    )


    if "*" in permisos:
        return True


    return correo.lower() in [
        x.lower()
        for x in permisos
    ]