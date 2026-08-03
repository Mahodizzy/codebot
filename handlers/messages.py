from handlers.admin import admin_mensajes

from telegram import Update
from telegram.ext import ContextTypes

from utils.estados import (
    obtener_estado,
    borrar_estado
)

from utils.permisos import (
    tiene_permiso_correo
)

from services.disney import (
    buscar_disney
)

from services.netflix import (
    buscar_netflix
)

from services.prime import (
    buscar_prime
)



async def recibir_mensaje(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    """
    Recibe mensajes normales del usuario.

    Ejemplo:
    usuario escribe:
    correo@gmail.com
    """

    user_id = update.effective_user.id

    await admin_mensajes(
        update,
        context
    )

    correo = (
        update.message.text
        .lower()
        .strip()
    )


    # Verificar si el usuario
    # eligió un servicio antes

    servicio = obtener_estado(
        user_id
    )


    if not servicio:

        await update.message.reply_text(
            "⚠️ Primero selecciona un servicio del menú."
        )

        return



    # Verificar permisos

    autorizado, mensaje = tiene_permiso_correo(
    user_id,
    correo
)


    if not autorizado:

        await update.message.reply_text(
            mensaje
        )

        borrar_estado(
            user_id
        )

        return



    await update.message.reply_text(
        "🔎 Buscando información, espera..."
    )



    resultado = None



    # ============================
    # DISNEY
    # ============================

    if servicio == "DISNEY":

        resultado = buscar_disney(
            correo
        )



    # ============================
    # NETFLIX
    # ============================

    elif servicio == "NETFLIX":

        resultado = buscar_netflix(
            correo
        )



    # ============================
    # PRIME
    # ============================

    elif servicio == "PRIME":

        resultado = buscar_prime(
            correo
        )



    # Limpiar estado después
    # de terminar la consulta

    borrar_estado(
        user_id
    )



    if not resultado:

        await update.message.reply_text(
            "⚠️ No se obtuvo respuesta."
        )

        return



    if not resultado.get(
        "encontrado"
    ):

        await update.message.reply_text(

            "❌ "
            + resultado.get(
                "mensaje",
                "No encontrado."
            )

        )

        return



    # ============================
    # RESPUESTAS EXITOSAS
    # ============================


    if servicio == "DISNEY":

        await update.message.reply_text(

            "✅ **CÓDIGO DISNEY+**\n\n"
            f"📧 `{correo}`\n"
            f"🔢 `{resultado['codigo']}`\n"
            f"📅 {resultado.get('fecha','')}",

            parse_mode="Markdown"

        )


    elif servicio == "PRIME":

        await update.message.reply_text(

            "✅ **CÓDIGO AMAZON PRIME**\n\n"
            f"📧 `{correo}`\n"
            f"🔢 `{resultado['codigo']}`\n"
            f"📅 {resultado.get('fecha','')}",

            parse_mode="Markdown"

        )


    elif servicio == "NETFLIX":

        await update.message.reply_text(

            "✅ **LINK NETFLIX ENCONTRADO**\n\n"
            f"📧 `{correo}`\n\n"
            f"🔗 {resultado['link']}",

            parse_mode="Markdown",

            disable_web_page_preview=True

        )