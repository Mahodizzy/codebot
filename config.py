"""
Configuración del bot.

Todas las claves se leen de variables de entorno.
En tu PC ponlas en un archivo .env (copia .env.example).
En el hosting (Render, Railway, etc.) ponlas en el panel de variables.
NUNCA escribas contraseñas o tokens directamente en este archivo.
"""

import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _requerida(nombre):
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise RuntimeError(
            f"Falta la variable de entorno {nombre}. "
            "Revisa tu archivo .env o la configuración del hosting."
        )
    return valor


# ==============================
# GMAIL
# ==============================
EMAIL_USER = _requerida("EMAIL_USER")
EMAIL_PASS = _requerida("EMAIL_PASS")
IMAP_SERVER = os.environ.get("IMAP_SERVER", "imap.gmail.com")

# ==============================
# TELEGRAM
# ==============================
TOKEN_TELEGRAM = _requerida("TOKEN_TELEGRAM")

# Uno o varios administradores separados por coma: 111,222
ADMIN_IDS = {
    int(x) for x in _requerida("ADMIN_ID").replace(" ", "").split(",") if x
}

# ==============================
# BASE DE DATOS
# ==============================
MONGO_URI = _requerida("MONGO_URI")
DATABASE_NAME = os.environ.get("DATABASE_NAME", "bot_gestion")

# ==============================
# BÚSQUEDA
# ==============================
# Solo se entregan códigos/links que llegaron en los últimos N minutos
MINUTOS_VALIDEZ = int(os.environ.get("MINUTOS_VALIDEZ", "20"))
