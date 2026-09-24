import logging

from config import MINUTOS_VALIDEZ
from services.gmail import (
    sesion_gmail, mensajes_para, obtener_html,
    extraer_links, formatear_fecha,
)

logger = logging.getLogger(__name__)

REMITENTE = "info@account.netflix.com"

# El asunto debe contener alguna de estas frases
ASUNTOS = ["acceso temporal", "temporary access"]

# El link debe contener alguna de estas palabras
PALABRAS_LINK = ["update", "travel", "verify"]


def buscar_netflix(correo):
    try:
        with sesion_gmail() as mail:
            hubo_correo = False
            for mensaje in mensajes_para(mail, REMITENTE, correo,
                                         MINUTOS_VALIDEZ, ASUNTOS):
                hubo_correo = True
                for link in extraer_links(obtener_html(mensaje)):
                    if "netflix.com" in link and any(p in link for p in PALABRAS_LINK):
                        return {"encontrado": True, "link": link,
                                "fecha": formatear_fecha(mensaje)}

        if hubo_correo:
            return {"encontrado": False, "mensaje":
                    "Llegó el correo de Netflix para esa cuenta, pero no encontré "
                    "el enlace. Avisa al administrador."}

        return {"encontrado": False, "mensaje":
                f"No hay correos de acceso temporal de Netflix de los últimos "
                f"{MINUTOS_VALIDEZ} minutos para esa cuenta. Solicítalo en el "
                "televisor y vuelve a intentar."}

    except Exception:
        logger.exception("Error buscando link Netflix para %s", correo)
        return {"encontrado": False, "mensaje":
                "No pude revisar el correo en este momento. Intenta en unos minutos."}
