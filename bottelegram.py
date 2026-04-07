import os
import datetime
import imaplib
import email
from email.header import decode_header
import re
import html
from threading import Thread
from flask import Flask
import requests

# Librerías de Telegram y MongoDB
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from pymongo import MongoClient

# --- CONFIGURACIÓN DE SERVIDOR PARA RENDER (KEEP ALIVE) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot de Gestión Online 24/7"

def run():
    app_web.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- CONFIGURACIÓN ---
EMAIL_USER = 'refills.ec@gmail.com'
EMAIL_PASS = 'cdzt etdq zxjr vlab'
IMAP_SERVER = 'imap.gmail.com'
TOKEN_TELEGRAM = os.environ.get('TOKEN_TELEGRAM')
ADMIN_ID = 1481058384

# CONEXIÓN MONGO DB (Reemplaza con tu URL real de Atlas)
MONGO_URI = os.environ.get('MONGO_URI')
client = MongoClient(MONGO_URI)
db_mongo = client['bot_gestion'] # Nombre de la base de datos
coleccion = db_mongo['usuarios'] # Nombre de la tabla

# --- GESTIÓN DE BASE DE DATOS MONGODB ---

def obtener_permisos(user_id):
    user = coleccion.find_one({"user_id": str(user_id)})
    if user:
        return user['permisos']
    # Si eres el admin y no estás, te creamos con acceso total
    if user_id == ADMIN_ID:
        coleccion.update_one({"user_id": str(ADMIN_ID)}, {"$set": {"permisos": ["*"]}}, upsert=True)
        return ["*"]
    return None

def tiene_permiso(user_id, correo_consultado):
    permisos = obtener_permisos(user_id)
    if permisos is None: return False, "🚫 No estás registrado en el sistema."
    if "*" in permisos: return True, ""
    if correo_consultado.lower() in [c.lower() for c in permisos]: return True, ""
    return False, f"⚠️ No tienes permiso para: {correo_consultado}"

# --- UTILIDADES ---
def limpiar_texto(texto):
    if not texto: return ""
    decodificado, encoding = decode_header(texto)[0]
    if isinstance(decodificado, bytes):
        return decodificado.decode(encoding if encoding else 'utf-8', errors='ignore')
    return decodificado

# --- COMANDOS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    mensaje = (
        "👋 **¡Bienvenido!**\n\n"
        "📜 **Comandos de Consulta:**\n"
        "▶️ `/codedisney [correo]`\n"
        "▶️ `/codenetflix [correo]`\n"
        "▶️ `/codeprime [correo]`\n"
        "▶️ `/correos` - Ver tus accesos."
    )
    if user_id == ADMIN_ID:
        mensaje += (
            "\n\n🛠 **Panel Admin:**\n"
            "▶️ `/registrar [ID] [correo]`\n"
            "▶️ `/usuarios` - Ver lista DB.\n"
            "▶️ `/eliminar [ID]` - Borrar usuario."
        )
    await update.message.reply_text(mensaje, parse_mode='Markdown')

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("❌ Uso: `/registrar [ID] [correo]`")
        return
    
    id_target, correo = str(context.args[0]), context.args[1].lower().strip()
    
    # Usamos $addToSet para evitar correos duplicados en el mismo ID
    coleccion.update_one(
        {"user_id": id_target},
        {"$addToSet": {"permisos": correo}},
        upsert=True
    )
    await update.message.reply_text(f"✅ Acceso concedido a `{id_target}` para `{correo}`", parse_mode='Markdown')

async def listar_usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    usuarios = coleccion.find()
    
    informe = "👥 **Usuarios en MongoDB:**\n\n"
    count = 0
    for u in usuarios:
        count += 1
        permisos = ", ".join(u['permisos'])
        informe += f"🆔 `{u['user_id']}`\n📧 `{permisos}`\n\n"
    
    if count == 0: informe = "📭 Base de datos vacía."
    await update.message.reply_text(informe, parse_mode='Markdown')

async def eliminar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID: return
    if not context.args: return
    id_del = str(context.args[0])
    coleccion.delete_one({"user_id": id_del})
    await update.message.reply_text(f"🗑️ ID `{id_del}` eliminado de la base de datos.")

async def ver_mis_correos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    permisos = obtener_permisos(user_id)
    if not permisos:
        await update.message.reply_text("🚫 No tienes cuentas asignadas.")
        return
    
    if "*" in permisos:
        await update.message.reply_text("🌟 Tienes acceso **TOTAL** (Admin).", parse_mode='Markdown')
    else:
        lista = "\n• ".join(permisos)
        await update.message.reply_text(f"📧 **Tus cuentas autorizadas:**\n\n• {lista}", parse_mode='Markdown')

# --- FUNCIONES DE EXTRACCIÓN (REUTILIZADAS Y OPTIMIZADAS) ---

async def get_disney(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args: return
    dest = context.args[0].lower().strip()
    ok, msg = tiene_permiso(user_id, dest)
    if not ok:
        await update.message.reply_text(msg); return

    await update.message.reply_text(f"🎬 Buscando Disney+ para: `{dest}`...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        criterio = f'(FROM "disneyplus@trx.mail2.disneyplus.com" SINCE "{datetime.datetime.now().strftime("%d-%b-%Y")}")'
        _, data = mail.search(None, criterio)
        ids = data[0].split()
        if not ids:
            await update.message.reply_text("❌ No hay correos hoy.")
        else:
            encontrado = False
            for m_id in reversed(ids):
                _, d = mail.fetch(m_id, '(RFC822)')
                msg_obj = email.message_from_bytes(d[0][1])
                if dest in str(msg_obj.get("To", "")).lower():
                    body = ""
                    if msg_obj.is_multipart():
                        for part in msg_obj.walk():
                            if part.get_content_type() == "text/html":
                                body = part.get_payload(decode=True).decode(errors='ignore'); break
                    else: body = msg_obj.get_payload(decode=True).decode(errors='ignore')
                    nums = re.findall(r'\b\d{6}\b', html.unescape(re.sub(r'<[^>]+>', '\n', body)))
                    cod = next((n for n in nums if n not in ["707070", "000000"]), None)
                    if cod:
                        await update.message.reply_text(f"✅ **DISNEY+**: `{cod}`", parse_mode='Markdown')
                        encontrado = True; break
            if not encontrado: await update.message.reply_text("❌ Código no hallado.")
        mail.logout()
    except Exception as e: await update.message.reply_text(f"⚠️ Error: {e}")

async def get_netflix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args: return
    dest = context.args[0].lower().strip()
    ok, msg = tiene_permiso(user_id, dest)
    if not ok:
        await update.message.reply_text(msg); return

    await update.message.reply_text(f"🎥 Buscando Netflix para: `{dest}`...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        criterio = f'(FROM "info@account.netflix.com" SINCE "{datetime.datetime.now().strftime("%d-%b-%Y")}")'
        _, data = mail.search(None, criterio)
        ids = data[0].split()
        if not ids:
            await update.message.reply_text("❌ No hay correos hoy.")
        else:
            encontrado = False
            for m_id in reversed(ids):
                _, d = mail.fetch(m_id, '(RFC822)')
                msg_obj = email.message_from_bytes(d[0][1])
                asu = limpiar_texto(msg_obj.get("Subject", ""))
                if dest in str(msg_obj.get("To", "")).lower() and "acceso temporal" in asu.lower():
                    payload = msg_obj.get_payload(decode=True).decode(errors='ignore') if not msg_obj.is_multipart() else ""
                    if msg_obj.is_multipart():
                        for part in msg_obj.walk():
                            if part.get_content_type() == "text/html":
                                payload = part.get_payload(decode=True).decode(errors='ignore'); break
                    body = payload.replace('=\r\n', '').replace('=\n', '')
                    links = re.findall(r'href=[\'"]?([^\'" >]+)', body)
                    url = next((l for l in links if "netflix.com" in l and ("update" in l or "travel" in l or "verify" in l)), None)
                    if url:
                        await update.message.reply_text(f"✅ **NETFLIX**: [SOLICITAR CÓDIGO]({url})", parse_mode='Markdown')
                        encontrado = True; break
            if not encontrado: await update.message.reply_text("❌ Link no hallado.")
        mail.logout()
    except Exception as e: await update.message.reply_text(f"⚠️ Error: {e}")

async def get_prime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if not context.args: return
    dest = context.args[0].lower().strip()
    ok, msg = tiene_permiso(user_id, dest)
    if not ok:
        await update.message.reply_text(msg); return

    await update.message.reply_text(f"📦 Buscando Amazon para: `{dest}`...")
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        criterio = f'(FROM "account-update@amazon.com" SINCE "{datetime.datetime.now().strftime("%d-%b-%Y")}")'
        _, data = mail.search(None, criterio)
        ids = data[0].split()
        if not ids:
            await update.message.reply_text("❌ No hay correos hoy.")
        else:
            encontrado = False
            for m_id in reversed(ids):
                _, d = mail.fetch(m_id, '(RFC822)')
                msg_obj = email.message_from_bytes(d[0][1])
                if dest in str(msg_obj.get("To", "")).lower():
                    body = ""
                    if msg_obj.is_multipart():
                        for part in msg_obj.walk():
                            if part.get_content_type() in ["text/plain", "text/html"]:
                                body += part.get_payload(decode=True).decode(errors='ignore')
                    else: body = msg_obj.get_payload(decode=True).decode(errors='ignore')
                    txt = html.unescape(re.sub(r'<[^>]+>', ' ', body))
                    match = re.search(r'verification code is:\s*(\d{6})', txt, re.IGNORECASE)
                    if match:
                        await update.message.reply_text(f"✅ **AMAZON**: `{match.group(1)}`", parse_mode='Markdown')
                        encontrado = True; break
            if not encontrado: await update.message.reply_text("❌ Código no hallado.")
        mail.logout()
    except Exception as e: await update.message.reply_text(f"⚠️ Error: {e}")

# --- ARRANQUE ---
if __name__ == '__main__':
    # 1. Configurar el puerto para Render
    port = int(os.environ.get("PORT", 5000))
    
    # 2. Iniciar el servidor Flask en segundo plano (reemplaza a keep_alive)
    from threading import Thread
    # Usamos 'app' si ese es el nombre de tu objeto Flask (e.g., app = Flask(__name__))
    Thread(target=lambda: app.run(host="0.0.0.0", port=port)).start()
    
    # 3. Configurar el Bot de Telegram (usaremos 'bot_app' para no confundir con Flask)
    bot_app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    
    # 4. Registrar los comandos
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("correos", ver_mis_correos))
    bot_app.add_handler(CommandHandler("usuarios", listar_usuarios))
    bot_app.add_handler(CommandHandler("registrar", registrar))
    bot_app.add_handler(CommandHandler("eliminar", eliminar))
    bot_app.add_handler(CommandHandler("codedisney", get_disney))
    bot_app.add_handler(CommandHandler("codenetflix", get_netflix))
    bot_app.add_handler(CommandHandler("codeprime", get_prime))
    
    # 5. Iniciar el bot
    print("🚀 Bot iniciado y servidor Flask corriendo en puerto", port)
    bot_app.run_polling()
