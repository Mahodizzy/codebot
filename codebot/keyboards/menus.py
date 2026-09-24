from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def menu_principal(es_admin=False):
    botones = [
        [InlineKeyboardButton("🎬 Disney+", callback_data="DISNEY")],
        [InlineKeyboardButton("🎥 Netflix", callback_data="NETFLIX")],
        [InlineKeyboardButton("📦 Prime Video", callback_data="PRIME")],
        [InlineKeyboardButton("📧 Mis cuentas", callback_data="CUENTAS")],
    ]
    if es_admin:
        botones.append([InlineKeyboardButton("🛠 Administración", callback_data="ADMIN")])
    return InlineKeyboardMarkup(botones)


def menu_admin():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👥 Usuarios", callback_data="ADM_LISTAR")],
        [InlineKeyboardButton("➕ Registrar / agregar correos", callback_data="ADM_REGISTRAR")],
        [InlineKeyboardButton("➖ Quitar un correo", callback_data="ADM_QUITAR")],
        [InlineKeyboardButton("🗑 Eliminar usuario", callback_data="ADM_ELIMINAR")],
        [InlineKeyboardButton("⬅️ Volver", callback_data="VOLVER")],
    ])


def boton_volver():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Menú principal", callback_data="VOLVER")]
    ])
