import imaplib
import email
from email.header import decode_header

from config import EMAIL_USER, EMAIL_PASS, IMAP_SERVER


def conectar_gmail():
    """
    Crea conexión con Gmail IMAP.
    Devuelve una sesión activa.
    """

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)

    mail.login(
        EMAIL_USER,
        EMAIL_PASS
    )

    mail.select("inbox")

    return mail



def cerrar_gmail(mail):
    """
    Cierra conexión con Gmail.
    """

    try:
        mail.logout()
    except:
        pass



def buscar_correos(mail, criterio):
    """
    Busca correos usando un criterio IMAP.

    Ejemplo:

    FROM "info@account.netflix.com"

    """

    status, data = mail.search(
        None,
        criterio
    )

    if status != "OK":
        return []

    return data[0].split()



def obtener_email(mail, mail_id):
    """
    Descarga un correo completo
    y devuelve el objeto email.
    """

    status, data = mail.fetch(
        mail_id,
        "(RFC822)"
    )

    if status != "OK":
        return None

    mensaje = email.message_from_bytes(
        data[0][1]
    )

    return mensaje



def limpiar_texto(texto):
    """
    Decodifica asuntos con caracteres especiales.
    
    Ejemplo:
    códigos con acentos o emojis.
    """

    if not texto:
        return ""

    decodificado, encoding = decode_header(texto)[0]

    if isinstance(decodificado, bytes):

        return decodificado.decode(
            encoding if encoding else "utf-8",
            errors="ignore"
        )

    return decodificado



def obtener_html(mensaje):
    """
    Extrae el contenido HTML de un correo.
    """

    body = ""

    if mensaje.is_multipart():

        for parte in mensaje.walk():

            if parte.get_content_type() == "text/html":

                body = parte.get_payload(
                    decode=True
                ).decode(
                    errors="ignore"
                )

                break

    else:

        body = mensaje.get_payload(
            decode=True
        ).decode(
            errors="ignore"
        )

    return body