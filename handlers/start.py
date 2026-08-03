from telegram import Update
from telegram.ext import ContextTypes

from keyboards.menus import menu_principal
from utils.permisos import es_admin



async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    """
    Comando /start

    Muestra el menú principal.
    """

    user_id = update.effective_user.id


    admin = es_admin(
        user_id
    )


    mensaje = (

        "👋 **¡Bienvenido a Bot Gestión V2!**\n\n"

        "Selecciona el servicio que deseas consultar:\n\n"

        "🎬 Disney+\n"
        "🎥 Netflix\n"
        "📦 Prime Video\n\n"

        "📧 También puedes revisar "
        "tus cuentas autorizadas."

    )


    await update.message.reply_text(

        mensaje,

        reply_markup=menu_principal(admin),

        parse_mode="Markdown"

    )