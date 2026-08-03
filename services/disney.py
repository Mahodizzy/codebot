import re
import html

from services.gmail import (
    conectar_gmail,
    buscar_correos,
    obtener_email,
    cerrar_gmail,
    obtener_html
)


def buscar_disney(destinatario_objetivo):
    """
    Busca códigos de acceso Disney+.

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


        # Remitente oficial de Disney+
        criterio = (
            '(FROM '
            '"disneyplus@trx.mail2.disneyplus.com")'
        )


        ids = buscar_correos(
            mail,
            criterio
        )


        if not ids:

            return {
                "encontrado": False,
                "mensaje": (
                    "No se encontró ningún "
                    "correo de Disney+."
                )
            }



        # Revisar correos desde el más nuevo

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



            # Confirmar que pertenece al correo solicitado

            if destinatario_objetivo.lower() not in para_quien:
                continue



            body = obtener_html(
                mensaje
            )


            if not body:
                continue



            # =============================
            # LIMPIEZA HTML
            # =============================


            body = re.sub(
                r'<(style|head|script)[^>]*>.*?</\1>',
                '',
                body,
                flags=re.DOTALL | re.IGNORECASE
            )


            texto_plano = html.unescape(
                re.sub(
                    r'<[^>]+>',
                    ' ',
                    body
                )
            )


            texto_plano = (
                " "
                .join(
                    texto_plano.split()
                )
            )



            # =============================
            # PATRONES DISNEY+
            # =============================


            patrones = [

                r'vencerá en 15 minutos\s*(\d{6})',

                r'código de acceso único[^\d]*(\d{6})',

                r'acceso para Disney\+[^\d]*(\d{6})',

                r'is:\s*(\d{6})'

            ]


            codigo = None



            for patron in patrones:

                encontrado = re.search(
                    patron,
                    texto_plano,
                    re.IGNORECASE
                )

                if encontrado:

                    codigo = encontrado.group(1)
                    break



            # =============================
            # BUSQUEDA DE RESPALDO
            # =============================

            if not codigo:


                numeros = re.findall(
                    r'\b\d{6}\b',
                    texto_plano
                )


                numeros_filtrados = [

                    n for n in numeros

                    if n not in [

                        "755059",
                        "202124",
                        "707070",
                        "000000",
                        "212024"

                    ]

                ]


                if numeros_filtrados:

                    codigo = numeros_filtrados[0]



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
                "pero no se pudo extraer "
                "el código Disney+."
            )

        }



    except Exception as e:


        return {

            "encontrado": False,

            "mensaje": (
                f"Error Disney: {str(e)}"
            )

        }



    finally:

        if mail:

            cerrar_gmail(mail)