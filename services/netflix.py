import re
import datetime

from services.gmail import (
    conectar_gmail,
    buscar_correos,
    obtener_email,
    cerrar_gmail,
    limpiar_texto
)


def buscar_netflix(destinatario_objetivo):
    """
    Busca el link de acceso temporal de Netflix
    para un correo autorizado.
    
    Retorna:
    {
        "encontrado": True/False,
        "link": "...",
        "fecha": "..."
    }
    """

    mail = None

    try:
        mail = conectar_gmail()

        fecha_hoy = datetime.datetime.now().strftime("%d-%b-%Y")

        criterio = (
            f'(FROM "info@account.netflix.com" '
            f'SINCE "{fecha_hoy}")'
        )

        ids = buscar_correos(
            mail,
            criterio
        )


        if not ids:

            return {
                "encontrado": False,
                "mensaje": "No hay correos de Netflix hoy."
            }


        for mail_id in reversed(ids):

            mensaje = obtener_email(
                mail,
                mail_id
            )

            if not mensaje:
                continue


            asunto = limpiar_texto(
                mensaje.get("Subject", "")
            )


            para_quien = str(
                mensaje.get("To", "")
            ).lower()


            # Verificar correo correcto
            # y asunto esperado

            if (
                destinatario_objetivo.lower()
                in para_quien
                and
                "acceso temporal"
                in asunto.lower()
            ):


                body = obtener_body_html(
                    mensaje
                )


                # Buscar enlaces dentro del HTML

                links = re.findall(
                    r'href=[\'"]?([^\'" >]+)',
                    body
                )


                url_final = None


                for link in links:

                    if (
                        "netflix.com" in link
                        and
                        (
                            "update" in link
                            or
                            "travel" in link
                            or
                            "verify" in link
                        )
                    ):

                        url_final = link
                        break



                if url_final:

                    return {
                        "encontrado": True,
                        "link": url_final,
                        "correo": destinatario_objetivo,
                        "fecha": mensaje.get("Date")
                    }



        return {
            "encontrado": False,
            "mensaje": (
                "Se encontró el correo, "
                "pero no el enlace válido."
            )
        }


    except Exception as e:

        return {
            "encontrado": False,
            "mensaje": f"Error Netflix: {str(e)}"
        }


    finally:

        if mail:
            cerrar_gmail(mail)



def obtener_body_html(mensaje):
    """
    Extrae HTML limpio del correo.
    """

    body = ""


    if mensaje.is_multipart():

        for parte in mensaje.walk():

            if parte.get_content_type() == "text/html":

                body = (
                    parte
                    .get_payload(
                        decode=True
                    )
                    .decode(
                        errors="ignore"
                    )
                )

                break


    else:

        body = (
            mensaje
            .get_payload(
                decode=True
            )
            .decode(
                errors="ignore"
            )
        )


    # Limpieza de saltos raros
    body = (
        body
        .replace("=\r\n", "")
        .replace("=\n", "")
    )


    return body