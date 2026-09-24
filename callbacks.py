import asyncio
import html

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from handlers.start import TEXTO_MENU
from keyboards.menus import menu_admin, menu_principal, boton_volver
from services.usuarios import obtener_correos
from utils.estados import guardar_servicio, borrar_todo
from utils.permisos import es_admin

NOMBRES = {
    "DISNEY": "🎬 Disney+",
    "NETFLIX": "🎥 Netflix",
    "PRIME": "📦 Prime Video",
}


async def callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    accion = query.data

    # ---------- SERVICIOS ----------
    if accion in NOMBRES:
        guardar_servicio(context, accion)
        await query.edit_message_text(
            f"{NOMBRES[accion]}\n\n"
            "📧 Escribe el correo de la cuenta:\n\n"
            "(escribe /cancelar para salir)"
        )
        return

    # ---------- MIS CUENTAS ----------
    if accion == "CUENTAS":
        if es_admin(user_id):
            texto = "🛠 Como administrador tienes acceso a todos los correos."
        else:
            correos = await asyncio.to_thread(obtener_correos, user_id)
            if not correos:
                texto = ("📭 No tienes correos autorizados.\n\n"
                         f"Tu ID de Telegram es <code>{user_id}</code>. "
                         "Envíaselo al administrador.")
            elif "*" in correos:
                texto = "✅ Tienes acceso a todos los correos."
            else:
                lista = "\n".join(f"• <code>{html.escape(c)}</code>" for c in correos)
                texto = f"📧 <b>Tus correos autorizados:</b>\n\n{lista}"

        await query.edit_message_text(
            texto, parse_mode=ParseMode.HTML, reply_markup=boton_volver()
        )
        return

    # ---------- PANEL ADMIN ----------
    if accion == "ADMIN":
        if not es_admin(user_id):
            await query.edit_message_text("🚫 No tienes acceso.")
            return
        borrar_todo(context)
        await query.edit_message_text("🛠 Panel de Administración", reply_markup=menu_admin())
        return

    # ---------- VOLVER ----------
    if accion == "VOLVER":
        borrar_todo(context)
        await query.edit_message_text(
            TEXTO_MENU,
            parse_mode=ParseMode.HTML,
            reply_markup=menu_principal(es_admin(user_id)),
        )
        return
