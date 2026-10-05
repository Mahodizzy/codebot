import asyncio
import html
import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from keyboards.menus import menu_admin
from services.usuarios import (
    listar_usuarios, registrar_usuario, quitar_correo, eliminar_usuario,
)
from utils.estados import (
    guardar_accion_admin, obtener_accion_admin, borrar_accion_admin,
)
from utils.permisos import es_admin
from utils.validacion import separar_id_y_correos

logger = logging.getLogger(__name__)

LIMITE_MENSAJE = 3800  # Telegram permite 4096 caracteres

INSTRUCCIONES = {
    "REGISTRAR": (
        "➕ <b>Registrar / agregar correos</b>\n\n"
        "Envíame el ID y los correos así:\n"
        "<code>ID_TELEGRAM|correo1@gmail.com, correo2@gmail.com</code>\n\n"
        "Si el usuario ya existe, los correos se suman a los que ya tiene.\n"
        "Usa <code>*</code> como correo para darle acceso a todos."
    ),
    "QUITAR": (
        "➖ <b>Quitar un correo</b>\n\n"
        "Envíame:\n<code>ID_TELEGRAM|correo@gmail.com</code>"
    ),
    "ELIMINAR": (
        "🗑 <b>Eliminar usuario</b>\n\n"
        "Envíame el ID del usuario que deseas eliminar por completo."
    ),
}


# ==================================
# BOTONES DEL PANEL
# ==================================

async def admin_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not es_admin(query.from_user.id):
        await query.edit_message_text("🚫 No tienes acceso.")
        return

    accion = query.data.removeprefix("ADM_")

    if accion == "LISTAR":
        usuarios = await asyncio.to_thread(listar_usuarios)
        partes = _armar_listado(usuarios)
        for i, parte in enumerate(partes):
            teclado = menu_admin() if i == len(partes) - 1 else None
            if i == 0:
                await query.edit_message_text(parte, parse_mode=ParseMode.HTML, reply_markup=teclado)
            else:
                await query.message.reply_text(parte, parse_mode=ParseMode.HTML, reply_markup=teclado)
        return

    if accion in INSTRUCCIONES:
        guardar_accion_admin(context, accion)
        await query.edit_message_text(
            INSTRUCCIONES[accion] + "\n\n(escribe /cancelar para salir)",
            parse_mode=ParseMode.HTML,
        )


def _armar_listado(usuarios):
    """Arma el listado dividido en partes que quepan en Telegram."""
    if not usuarios:
        return ["📂 No hay usuarios registrados."]

    partes = []
    actual = f"👥 <b>Usuarios registrados ({len(usuarios)})</b>\n"

    for u in usuarios:
        correos = u.get("permisos") or []
        if isinstance(correos, str):
            correos = [correos]

        lineas = [f"🆔 <code>{html.escape(str(u.get('user_id', '?')))}</code>"]
        if correos:
            lineas += [f"   • {html.escape(c)}" for c in correos]
        else:
            lineas.append("   Sin correos registrados")
        bloque = "\n".join(lineas)

        if len(actual) + len(bloque) + 2 > LIMITE_MENSAJE:
            partes.append(actual)
            actual = ""
        actual += "\n" + bloque + "\n"

    partes.append(actual)
    return partes


# ==================================
# MENSAJES DEL ADMIN
# ==================================

def _registrar(texto):
    user_id, correos = separar_id_y_correos(texto)
    finales = registrar_usuario(user_id, correos)
    lista = "\n".join(f"   • {html.escape(c)}" for c in finales)
    return f"✅ Acceso guardado para <code>{user_id}</code>.\n\nCorreos actuales:\n{lista}"


def _quitar(texto):
    user_id, correos = separar_id_y_correos(texto)
    quitados = [c for c in correos if quitar_correo(user_id, c)]
    if not quitados:
        return f"⚠️ El usuario <code>{user_id}</code> no tenía esos correos."
    return (f"➖ Se quitaron de <code>{user_id}</code>:\n"
            + "\n".join(f"   • {html.escape(c)}" for c in quitados))


def _eliminar(texto):
    user_id = texto.strip()
    if not user_id.isdigit():
        raise ValueError("El ID de Telegram debe tener solo números.")
    if eliminar_usuario(user_id):
        return f"🗑 Usuario <code>{user_id}</code> eliminado."
    return f"⚠️ No existe ningún usuario con ID <code>{user_id}</code>."


ACCIONES = {"REGISTRAR": _registrar, "QUITAR": _quitar, "ELIMINAR": _eliminar}


async def procesar_mensaje_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Si el admin tiene una acción pendiente, la procesa y devuelve True.
    Si no, devuelve False para que el mensaje siga como consulta normal.
    """
    accion = obtener_accion_admin(context)
    if accion not in ACCIONES:
        return False

    texto = update.message.text.strip()

    try:
        respuesta = await asyncio.to_thread(ACCIONES[accion], texto)
    except ValueError as error:
        # Dato mal escrito: se mantiene la acción para que lo intente de nuevo
        await update.message.reply_text(
            f"⚠️ {html.escape(str(error))}\n\nIntenta de nuevo o escribe /cancelar.",
            parse_mode=ParseMode.HTML,
        )
        return True
    except Exception:
        logger.exception("Error en acción de admin %s", accion)
        borrar_accion_admin(context)
        await update.message.reply_text(
            "❌ No se pudo guardar en la base de datos. Revisa los logs del servidor.",
            reply_markup=menu_admin(),
        )
        return True

    borrar_accion_admin(context)
    await update.message.reply_text(respuesta, parse_mode=ParseMode.HTML, reply_markup=menu_admin())
    return True
