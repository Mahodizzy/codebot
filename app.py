import os
import asyncio

from threading import Thread

from flask import Flask

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)


from config import TOKEN_TELEGRAM


from handlers.start import start

from handlers.callbacks import callbacks

from handlers.messages import recibir_mensaje
from handlers.admin import (
    admin_callbacks,
    admin_mensajes
)



# ==================================
# SERVIDOR FLASK PARA RENDER
# ==================================

app = Flask(__name__)



@app.route("/")
def home():

    return (
        "Bot de Gestión V2 "
        "de Refills EC está Vivo 🚀"
    )



def iniciar_flask():

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )


    app.run(

        host="0.0.0.0",

        port=port,

        debug=False,

        use_reloader=False

    )


# ==================================
# ARRANQUE DEL BOT
# ==================================

def iniciar_bot():

    bot_app = (
        ApplicationBuilder()
        .token(
            TOKEN_TELEGRAM
        )
        .build()
    )


    # ===============================
    # COMANDOS
    # ===============================

    bot_app.add_handler(

        CommandHandler(
            "start",
            start
        )

    )


    # ===============================
    # BOTONES ADMIN
    # ===============================

    bot_app.add_handler(

        CallbackQueryHandler(
            admin_callbacks,
            pattern="^(LISTAR_USUARIOS|REGISTRAR|ELIMINAR)$"
        )

    )


    # ===============================
    # BOTONES SERVICIOS
    # ===============================

    bot_app.add_handler(

        CallbackQueryHandler(
            callbacks
        )

    )


    # ===============================
    # MENSAJES ADMIN
    # ===============================

    bot_app.add_handler(

        MessageHandler(

            filters.TEXT
            & ~filters.COMMAND,

            admin_mensajes

        ),

        group=0

    )


    # ===============================
    # MENSAJES USUARIO
    # ===============================

    bot_app.add_handler(

        MessageHandler(

            filters.TEXT
            & ~filters.COMMAND,

            recibir_mensaje

        ),

        group=1

    )


    print(
        "🚀 Bot V2 iniciado correctamente"
    )


    import asyncio

asyncio.set_event_loop(
    asyncio.new_event_loop()
)

bot_app.run_polling()

# ==================================
# EJECUCIÓN
# ==================================


if __name__ == "__main__":


    Thread(

        target=iniciar_flask

    ).start()



    iniciar_bot()
