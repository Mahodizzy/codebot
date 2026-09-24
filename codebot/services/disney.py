import logging

from config import MINUTOS_VALIDEZ
from services.gmail import (
    sesion_gmail, mensajes_para, obtener_html,
    html_a_texto, extraer_codigo, formatear_fecha,
)

logger = logging.getLogger(__name__)

REMITENTE = "disneyplus@trx.mail2.disneyplus.com"

PATRONES = [
    r"vencerá en 15 minutos\s*(\d{6})",
    r"código de acceso único[^\d]*(\d{6})",
    r"acceso para Disney\+[^\d]*(\d{6})",
    r"is:\s*(\d{6})",
]

IGNORADOS = {"755059", "202124", "707070", "000000", "212024"}


def buscar_disney(correo):
    try:
        with sesion_gmail() as mail:
            hubo_correo = False
            for mensaje in mensajes_para(mail, REMITENTE, correo, MINUTOS_VALIDEZ):
                hubo_correo = True
                texto = html_a_texto(obtener_html(mensaje))
                codigo = extraer_codigo(texto, PATRONES, IGNORADOS)
                if codigo:
                    return {"encontrado": True, "codigo": codigo,
                            "fecha": formatear_fecha(mensaje)}

        if hubo_correo:
            return {"encontrado": False, "mensaje":
                    "Llegó un correo de Disney+ para esa cuenta, pero no pude leer "
                    "el código. Avisa al administrador."}

        return {"encontrado": False, "mensaje":
                f"No hay códigos de Disney+ de los últimos {MINUTOS_VALIDEZ} minutos "
                "para esa cuenta. Pide el código en Disney+ y vuelve a intentar."}

    except Exception:
        logger.exception("Error buscando código Disney+ para %s", correo)
        return {"encontrado": False, "mensaje":
                "No pude revisar el correo en este momento. Intenta en unos minutos."}
