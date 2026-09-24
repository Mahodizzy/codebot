"""
Funciones comunes para leer el Gmail por IMAP.
Las usan disney.py, netflix.py y prime.py.
"""

import email
import html
import imaplib
import re
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from email.header import decode_header, make_header
from email.utils import getaddresses, parsedate_to_datetime

from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER

ZONA_ECUADOR = timezone(timedelta(hours=-5))
MESES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Máximo de correos recientes que se revisan por búsqueda
MAX_REVISAR = 50


# ==============================
# CONEXIÓN
# ==============================

@contextmanager
def sesion_gmail():
    """
    Abre Gmail en modo solo lectura (no marca correos como leídos)
    y siempre cierra la conexión al terminar.
    """
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, timeout=30)
    try:
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("INBOX", readonly=True)
        yield mail
    finally:
        try:
            mail.logout()
        except Exception:
            pass


# ==============================
# BÚSQUEDA
# ==============================

def _fecha_imap(fecha):
    # Se arma a mano para no depender del idioma del servidor
    return f"{fecha.day:02d}-{MESES[fecha.month - 1]}-{fecha.year}"


def buscar_ids(mail, remitente, dias=1):
    """IDs de correos del remitente desde hace `dias` días (incluye ayer por la diferencia horaria)."""
    desde = datetime.now(timezone.utc) - timedelta(days=dias)
    status, data = mail.search(None, "FROM", f'"{remitente}"', "SINCE", _fecha_imap(desde))
    if status != "OK" or not data or not data[0]:
        return []
    return data[0].split()


def _fetch(mail, mail_id, partes):
    status, data = mail.fetch(mail_id, partes)
    if status != "OK" or not data:
        return None
    for item in data:
        if isinstance(item, tuple) and len(item) >= 2:
            return email.message_from_bytes(item[1])
    return None


def obtener_cabeceras(mail, mail_id):
    """Descarga solo las cabeceras (rápido)."""
    return _fetch(mail, mail_id, "(BODY.PEEK[HEADER.FIELDS (TO CC DATE SUBJECT)])")


def obtener_email(mail, mail_id):
    """Descarga el correo completo sin marcarlo como leído."""
    return _fetch(mail, mail_id, "(BODY.PEEK[])")


def mensajes_para(mail, remitente, correo, minutos, palabras_asunto=None):
    """
    Devuelve (del más nuevo al más viejo) los correos completos que:
    - vienen del remitente
    - llegaron hace menos de `minutos`
    - van dirigidos EXACTAMENTE a `correo`
    - (opcional) tienen alguna de las palabras en el asunto
    """
    ids = buscar_ids(mail, remitente)

    for mail_id in list(reversed(ids))[:MAX_REVISAR]:
        cabeceras = obtener_cabeceras(mail, mail_id)
        if cabeceras is None:
            continue
        if not es_reciente(cabeceras, minutos):
            continue
        if not destinatario_coincide(cabeceras, correo):
            continue
        if palabras_asunto:
            asunto = decodificar_cabecera(cabeceras.get("Subject")).lower()
            if not any(p in asunto for p in palabras_asunto):
                continue

        completo = obtener_email(mail, mail_id)
        if completo is not None:
            yield completo


# ==============================
# CABECERAS
# ==============================

def decodificar_cabecera(valor):
    """Decodifica asuntos con tildes o emojis, aunque vengan en varias partes."""
    if not valor:
        return ""
    try:
        return str(make_header(decode_header(valor)))
    except Exception:
        return str(valor)


def destinatario_coincide(mensaje, correo):
    """Compara la dirección EXACTA (ana@gmail.com no coincide con mariana@gmail.com)."""
    correo = correo.strip().lower()
    campos = (mensaje.get_all("To") or []) + (mensaje.get_all("Cc") or [])
    for _, direccion in getaddresses(campos):
        if direccion.strip().lower() == correo:
            return True
    return False


def fecha_mensaje(mensaje):
    try:
        fecha = parsedate_to_datetime(mensaje.get("Date"))
    except (TypeError, ValueError, IndexError):
        return None
    if fecha is None:
        return None
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=timezone.utc)
    return fecha


def es_reciente(mensaje, minutos):
    fecha = fecha_mensaje(mensaje)
    if fecha is None:
        return False
    return datetime.now(timezone.utc) - fecha <= timedelta(minutes=minutos)


def formatear_fecha(mensaje):
    """Fecha del correo en hora de Ecuador: 23/09/2026 14:05"""
    fecha = fecha_mensaje(mensaje)
    if fecha is None:
        return ""
    return fecha.astimezone(ZONA_ECUADOR).strftime("%d/%m/%Y %H:%M")


# ==============================
# CONTENIDO
# ==============================

def _decodificar_parte(parte):
    datos = parte.get_payload(decode=True)
    if not datos:
        return ""
    charset = parte.get_content_charset() or "utf-8"
    try:
        return datos.decode(charset, errors="replace")
    except LookupError:
        return datos.decode("utf-8", errors="replace")


def obtener_html(mensaje):
    """Devuelve el HTML del correo (o el texto plano si no tiene HTML)."""
    texto_plano = ""
    for parte in mensaje.walk():
        if parte.is_multipart():
            continue
        tipo = parte.get_content_type()
        if tipo == "text/html":
            return _decodificar_parte(parte)
        if tipo == "text/plain" and not texto_plano:
            texto_plano = _decodificar_parte(parte)
    return texto_plano


def html_a_texto(body):
    """Quita etiquetas, estilos y scripts; deja texto en una sola línea."""
    body = re.sub(r"<(style|head|script)[^>]*>.*?</\1>", " ", body,
                  flags=re.DOTALL | re.IGNORECASE)
    texto = html.unescape(re.sub(r"<[^>]+>", " ", body))
    return " ".join(texto.split())


def extraer_links(body):
    """Todos los href del HTML, ya decodificados (&amp; -> &)."""
    links = re.findall(r'href\s*=\s*["\']([^"\']+)["\']', body, re.IGNORECASE)
    return [html.unescape(link).strip() for link in links]


def extraer_codigo(texto, patrones, ignorados=()):
    """
    1) Busca el código con los patrones conocidos.
    2) Si no, solo acepta un número de 6 dígitos si hay UNO solo
       en el correo (para no entregar un número equivocado).
    """
    for patron in patrones:
        encontrado = re.search(patron, texto, re.IGNORECASE)
        if encontrado:
            return encontrado.group(1)

    candidatos = {n for n in re.findall(r"\b\d{6}\b", texto) if n not in ignorados}
    if len(candidatos) == 1:
        return candidatos.pop()
    return None
