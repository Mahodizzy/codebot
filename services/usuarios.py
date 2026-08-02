from services.database.mongo import usuarios



def registrar_usuario(
    user_id,
    correo
):

    usuario = usuarios.find_one(
        {
            "user_id": str(user_id)
        }
    )


    if usuario:


        usuarios.update_one(

            {
                "user_id": str(user_id)
            },

            {
                "$addToSet":
                {
                    "correos": correo
                }
            }

        )


    else:


        usuarios.insert_one(

            {
                "user_id": str(user_id),
                "correos": [
                    correo
                ],
                "permisos":
                [
                    "DISNEY",
                    "NETFLIX",
                    "PRIME"
                ]
            }

        )





def listar_usuarios():

    return list(
        usuarios.find({})
    )





def eliminar_usuario(
    user_id
):

    usuarios.delete_one(

        {
            "user_id": str(user_id)
        }

    )
