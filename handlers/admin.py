from telegram import Update
from telegram.ext import ContextTypes

from services.usuarios import (
    listar_usuarios,
    registrar_usuario,
    eliminar_usuario
)

from utils.permisos import es_admin


# estados temporales del administrador

admin_estado = {}



async def admin_callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    user_id = query.from_user.id


    if not es_admin(user_id):

        await query.edit_message_text(
            "🚫 No tienes acceso."
        )

        return
    accion = query.data


    if accion == "LISTAR_USUARIOS":

        usuarios = listar_usuarios()


        if not usuarios:

            texto = (
                "📂 No hay usuarios registrados."
            )

        else:

            texto = "👥 Usuarios registrados:\n\n"

            for u in usuarios:

                texto += (
                    f"🆔 ID: {u['user_id']}\n"
                    f"📧 Correos permitidos:\n"
                )

                correos = u.get(
                    "correos",
                    u.get(
                        "permisos",
                        []
                    )
                )

                if correos:

                    for correo in correos:

                        texto += (
                            f"   • {correo}\n"
                        )

                else:

                    texto += (
                        "   Sin correos registrados\n"
                    )


                texto += "\n"



        await query.edit_message_text(
            texto
        )


        return





   
    if accion == "REGISTRAR":


        admin_estado[user_id] = "registrar"


        await query.edit_message_text(

            "➕ Envíame los datos así:\n\n"
            "ID_TELEGRAM|correo@gmail.com\n\n"
            "Ejemplo:\n"
            "123456789|cliente@gmail.com"

        )

        return



    if accion == "ELIMINAR":


        admin_estado[user_id] = "eliminar"


        await query.edit_message_text(

            "🗑 Envíame el ID del usuario que deseas eliminar."

        )

        return





async def admin_mensajes(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):


    user_id = update.effective_user.id


    if user_id not in admin_estado:

        return



    accion = admin_estado[user_id]


    texto = update.message.text.strip()



    if accion == "registrar":


        try:

            telegram_id, correo = texto.split("|")


            registrar_usuario(
                telegram_id,
                correo
            )


            await update.message.reply_text(
                "✅ Usuario registrado correctamente."
            )


        except Exception as e:


            await update.message.reply_text(
                f"❌ Error: {e}"
            )



    elif accion == "eliminar":


        eliminar_usuario(
            texto
        )


        await update.message.reply_text(
            "🗑 Usuario eliminado."
        )



    del admin_estado[user_id]
  