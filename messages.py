import asyncio
import html

from telegram import LinkPreviewOptions, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.admin import procesar_mensaje_admin
from keyboards.menus import boton_volver
from services.disney import buscar_disney
from services.netflix import buscar_netflix
from services.prime import buscar_prime
from utils.estados import obtener_servicio, borrar_servicio
from utils.permisos import es_admin, tiene_permiso_correo
from utils.validacion import es_correo_valido

BUSCADORES = {
    "DISNEY": buscar_disney,
    "NETFLIX": buscar_netflix,
    "PRIME": buscar_prime,
}

TITULOS = {
    "DISNEY": "CÓDIGO DISNEY+",
    "NETFLIX": "LINK NETFLIX ENCONTRADO",
    "PRIME": "CÓDIGO AMAZON PRIME",
}


async def recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    user_id = update.effective_user.id

    # 1) Si el admin está registrando/eliminando, eso tiene prioridad
    if es_admin(user_id) and await procesar_mensaje_admin(update, context):
        return

    # 2) El usuario debe haber elegido un servicio
    servicio = obtener_servicio(context)
    if not servicio:
        await update.message.reply_text("⚠️ Primero selecciona un servicio con /start.")
        return

    correo = update.message.text.strip().lower()

    if not es_correo_valido(correo):
        await update.message.reply_text(
            "⚠️ Eso no parece un correo. Escríbelo de nuevo, por ejemplo: "
            "cliente@gmail.com\n(o /cancelar para salir)"
        )
        return

    # 3) Permisos
    autorizado, mensaje = await asyncio.to_thread(tiene_permiso_correo, user_id, correo)
    borrar_servicio(context)

    if not autorizado:
        await update.message.reply_text(mensaje, reply_markup=boton_volver())
        return

    # 4) Búsqueda en segundo plano (el bot sigue atendiendo a los demás)
    espera = await update.message.reply_text("🔎 Buscando, espera un momento...")
    resultado = await asyncio.to_thread(BUSCADORES[servicio], correo)

    await espera.edit_text(
        _formatear_respuesta(servicio, correo, resultado),
        parse_mode=ParseMode.HTML,
        link_preview_options=LinkPreviewOptions(is_disabled=True),
        reply_markup=boton_volver(),
    )


def _formatear_respuesta(servicio, correo, resultado):
    if not resultado or not resultado.get("encontrado"):
        mensaje = (resultado or {}).get("mensaje", "No se obtuvo respuesta.")
        return "❌ " + html.escape(mensaje)

    lineas = [
        f"✅ <b>{TITULOS[servicio]}</b>",
        "",
        f"📧 <code>{html.escape(correo)}</code>",
    ]

    if servicio == "NETFLIX":
        link = html.escape(resultado["link"], quote=True)
        lineas += ["", f'🔗 <a href="{link}">Toca aquí para abrir el enlace</a>']
    else:
        lineas.append(f"🔢 <code>{html.escape(resultado['codigo'])}</code>")

    if resultado.get("fecha"):
        lineas.append(f"📅 {html.escape(resultado['fecha'])} (hora Ecuador)")

    return "\n".join(lineas)
