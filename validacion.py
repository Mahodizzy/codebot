import re

PATRON_CORREO = re.compile(r"^[^@\s|]+@[^@\s|]+\.[^@\s|]+$")


def es_correo_valido(texto):
    return bool(PATRON_CORREO.match(texto.strip()))


def separar_id_y_correos(texto):
    """
    "123456789 | a@gmail.com, b@gmail.com"  ->  ("123456789", ["a@gmail.com", "b@gmail.com"])
    Lanza ValueError con un mensaje claro si algo está mal.
    """
    if "|" not in texto:
        raise ValueError("Falta el separador |. Formato: ID|correo@gmail.com")

    id_txt, correos_txt = texto.split("|", 1)
    user_id = id_txt.strip()

    if not user_id.isdigit():
        raise ValueError("El ID de Telegram debe tener solo números.")

    correos = [c.strip().lower() for c in re.split(r"[,;\s]+", correos_txt) if c.strip()]
    if not correos:
        raise ValueError("No escribiste ningún correo.")

    invalidos = [c for c in correos if c != "*" and not es_correo_valido(c)]
    if invalidos:
        raise ValueError("Estos correos no son válidos: " + ", ".join(invalidos))

    return user_id, correos
