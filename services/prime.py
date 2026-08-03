import re
import html

from services.gmail import (
    conectar_gmail,
    buscar_correos,
    obtener_email,
    cerrar_gmail,
    obtener_html
)


def buscar_prime(destinatario_objetivo):
    """
    Busca códigos de Amazon Prime.

    Retorna:

    {
        "encontrado": True,
        "codigo": "123456",
        "fecha": "..."
    }

    o

    {
        "encontrado": False,
        "mensaje": "..."
    }
    """

    mail = None

    try:

        mail = conectar_gmail()


        # Remitente oficial de Amazon
        criterio = (
            '(FROM "account-update@amazon.com")'
        )


        ids = buscar_correos(
            mail,
            criterio
        )


        if not ids:

            return {

                "encontrado": False,

                "mensaje": (
                    "No se encontró "
                    "ningún correo de Amazon."
                )

            }



        # Revisar desde el correo más reciente

        for mail_id in reversed(ids):


            mensaje = obtener_email(
                mail,
                mail_id
            )


            if not mensaje:
                continue



            para_quien = str(
                mensaje.get("To", "")
            ).lower()



            # Verificar destinatario

            if destinatario_objetivo.lower() not in para_quien:

                continue



            body = obtener_html(
                mensaje
            )


            if not body:

                continue



            # ============================
            # LIMPIEZA HTML
            # ============================


            body = re.sub(

                r'<(style|head|script)[^>]*>.*?</\1>',

                '',

                body,

                flags=re.DOTALL | re.IGNORECASE

            )


            texto_limpio = html.unescape(

                re.sub(

                    r'<[^>]+>',

                    ' ',

                    body

                )

            )


            texto_limpio = (

                " "

                .join(

                    texto_limpio.split()

                )

            )



            # ============================
            # PATRONES AMAZON
            # ============================


            patrones = [

                r'code is:\s*(\d{6})',

                r'código es:\s*(\d{6})',

                r'verification code:\s*(\d{6})',

                r'código de verificación:\s*(\d{6})'

            ]


            codigo = None



            for patron in patrones:


                resultado = re.search(

                    patron,

                    texto_limpio,

                    re.IGNORECASE

                )


                if resultado:


                    codigo = resultado.group(1)

                    break



            # ============================
            # BUSQUEDA DE RESPALDO
            # ============================


            if not codigo:


                numeros = re.findall(

                    r'\b\d{6}\b',

                    texto_limpio

                )


                filtros = [

                    "202124",

                    "755059",

                    "000000"

                ]


                for numero in numeros:


                    if numero not in filtros:


                        codigo = numero

                        break



            if codigo:


                return {


                    "encontrado": True,


                    "codigo": codigo,


                    "correo": destinatario_objetivo,


                    "fecha": mensaje.get("Date")


                }



        return {


            "encontrado": False,


            "mensaje": (

                "Se encontró el correo "

                "pero no un código válido."

            )


        }



    except Exception as e:


        return {


            "encontrado": False,


            "mensaje": f"Error Prime: {str(e)}"


        }



    finally:


        if mail:

            cerrar_gmail(mail)
            