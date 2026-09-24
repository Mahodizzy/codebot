import asyncio
import logging
import os
from threading import Thread

from flask import Flask
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from config import TOKEN_TELEGRAM
from handlers.admin import admin_callbacks
from handlers.callbacks import callbacks
from handlers.messages import recibir_mensaje
from handlers.start import start, cancelar
from services.usuarios import preparar_base_datos

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
# httpx escribe en el log las URLs de Telegram, que incluyen el TOKEN
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger("bot")


# ==================================
# SERVIDOR FLASK (mantiene vivo el hosting)
# ==================================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot de Gestión V2 de Refills EC está Vivo 🚀"


def iniciar_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


# ==================================
# BOT TELEGRAM
# ==================================

async def manejar_error(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Error procesando una actualización", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Ocurrió un error inesperado. Intenta de nuevo con /start."
            )
        except Exception:
            pass


def iniciar_bot():
    # Event loop propio (necesario en Python 3.14+)
    asyncio.set_event_loop(asyncio.new_event_loop())

    bot_app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()

    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("cancelar", cancelar))

    bot_app.add_handler(CallbackQueryHandler(admin_callbacks, pattern=r"^ADM_"))
    bot_app.add_handler(CallbackQueryHandler(callbacks))

    # Solo chats privados: en un grupo todos verían los códigos
    bot_app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND & filters.ChatType.PRIVATE,
        recibir_mensaje,
    ))

    bot_app.add_error_handler(manejar_error)

    logger.info("🚀 Bot V2 iniciado correctamente")
    bot_app.run_polling(close_loop=False)


if __name__ == "__main__":
    try:
        preparar_base_datos()
    except Exception:
        logger.exception("No se pudo preparar la base de datos (el bot arranca igual)")

    Thread(target=iniciar_flask, daemon=True).start()
    iniciar_bot()
