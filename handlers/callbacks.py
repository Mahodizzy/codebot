from handlers.admin import admin_callbacks
from telegram import Update
from telegram.ext import ContextTypes

from utils.estados import guardar_estado
from keyboards.menus import menu_admin, menu_principal
from utils.permisos import es_admin



async def callbacks(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    """
    Controla todos los botones
    del menú principal.
    """


    query = update.callback_query


    await query.answer()


    user_id = query.from_user.id


    accion = query.data


    if accion in [
        "LISTAR_USUARIOS",
        "REGISTRAR",
        "ELIMINAR"
    ]:

        await admin_callbacks(
            update,
            context
        )

        return



    # ============================
    # SERVICIOS
    # ============================


    if accion in [
        "DISNEY",
        "NETFLIX",
        "PRIME"
    ]:


        guardar_estado(
            user_id,
            accion
        )


        nombres = {

            "DISNEY": "🎬 Disney+",

            "NETFLIX": "🎥 Netflix",

            "PRIME": "📦 Prime Video"

        }


        await query.edit_message_text(

            f"{nombres[accion]}\n\n"
            "📧 Escribe el correo autorizado:",

        )


        return



    # ============================
    # MIS CUENTAS
    # ============================


    if accion == "CUENTAS":


        await query.edit_message_text(

            "📧 La opción de cuentas "
            "estará disponible pronto."

        )


        return



    # ============================
    # PANEL ADMIN
    # ============================


    if accion == "ADMIN":


        if not es_admin(user_id):

            await query.edit_message_text(
                "🚫 No tienes acceso."
            )

            return



        await query.edit_message_text(

            "🛠 Panel de Administración",

            reply_markup=menu_admin()

        )


        return



    # ============================
    # VOLVER
    # ============================


    if accion == "VOLVER":


        await query.edit_message_text(

            "👋 Menú principal:",

            reply_markup=menu_principal(
                es_admin(user_id)
            )

        )


        return
