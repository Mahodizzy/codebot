from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from keyboards.menus import menu_principal
from utils.estados import borrar_todo
from utils.permisos import es_admin

TEXTO_MENU = (
    "👋 <b>¡Bienvenido a Bot Gestión V2!</b>\n\n"
    "Selecciona el servicio que deseas consultar:\n\n"
    "🎬 Disney+\n"
    "🎥 Netflix\n"
    "📦 Prime Video\n\n"
    "📧 En <b>Mis cuentas</b> ves tus correos autorizados."
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    borrar_todo(context)
    await update.message.reply_text(
        TEXTO_MENU,
        parse_mode=ParseMode.HTML,
        reply_markup=menu_principal(es_admin(update.effective_user.id)),
    )


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    borrar_todo(context)
    await update.message.reply_text(
        "❎ Operación cancelada.",
        reply_markup=menu_principal(es_admin(update.effective_user.id)),
    )
