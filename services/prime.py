import logging

from config import MINUTOS_VALIDEZ
from services.gmail import (
    sesion_gmail, mensajes_para, obtener_html,
    html_a_texto, extraer_codigo, formatear_fecha,
)

logger = logging.getLogger(__name__)

REMITENTE = "account-update@amazon.com"

PATRONES = [
    r"code is:\s*(\d{6})",
    r"código es:\s*(\d{6})",
    r"verification code:\s*(\d{6})",
    r"código de verificación(?: es)?:\s*(\d{6})",
]

IGNORADOS = {"202124", "755059", "000000"}


def buscar_prime(correo):
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
                    "Llegó un correo de Amazon para esa cuenta, pero no pude leer "
                    "el código. Avisa al administrador."}

        return {"encontrado": False, "mensaje":
                f"No hay códigos de Amazon de los últimos {MINUTOS_VALIDEZ} minutos "
                "para esa cuenta. Pide el código en Prime Video y vuelve a intentar."}

    except Exception:
        logger.exception("Error buscando código Prime para %s", correo)
        return {"encontrado": False, "mensaje":
                "No pude revisar el correo en este momento. Intenta en unos minutos."}
