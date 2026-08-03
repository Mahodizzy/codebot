from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def menu_principal(es_admin=False):
    """
    Menú principal del bot.
    """

    botones = [

        [
            InlineKeyboardButton(
                "🎬 Disney+",
                callback_data="DISNEY"
            )
        ],

        [
            InlineKeyboardButton(
                "🎥 Netflix",
                callback_data="NETFLIX"
            )
        ],

        [
            InlineKeyboardButton(
                "📦 Prime Video",
                callback_data="PRIME"
            )
        ],

        [
            InlineKeyboardButton(
                "📧 Mis cuentas",
                callback_data="CUENTAS"
            )
        ]

    ]


    # Si es administrador,
    # agregamos panel admin

    if es_admin:

        botones.append(

            [
                InlineKeyboardButton(
                    "🛠 Administración",
                    callback_data="ADMIN"
                )
            ]

        )


    return InlineKeyboardMarkup(
        botones
    )



def menu_admin():

    """
    Menú exclusivo administrador.
    """

    botones = [

        [

            InlineKeyboardButton(
                "👥 Usuarios",
                callback_data="LISTAR_USUARIOS"
            )

        ],

        [

            InlineKeyboardButton(
                "➕ Registrar acceso",
                callback_data="REGISTRAR"
            )

        ],

        [

            InlineKeyboardButton(
                "🗑 Eliminar usuario",
                callback_data="ELIMINAR"
            )

        ],

        [

            InlineKeyboardButton(
                "⬅️ Volver",
                callback_data="VOLVER"
            )

        ]

    ]


    return InlineKeyboardMarkup(
        botones
    )



def boton_volver():

    """
    Botón volver al menú principal.
    """

    return InlineKeyboardMarkup(

        [

            [

                InlineKeyboardButton(
                    "⬅️ Volver",
                    callback_data="VOLVER"
                )

            ]

        ]

    )