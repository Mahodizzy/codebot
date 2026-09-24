"""
Qué está esperando el bot de cada usuario.
Se guarda en context.user_data (uno por usuario, lo maneja Telegram).
"""

SERVICIO = "servicio"          # DISNEY / NETFLIX / PRIME
ACCION_ADMIN = "accion_admin"  # REGISTRAR / QUITAR / ELIMINAR


def guardar_servicio(context, servicio):
    context.user_data.pop(ACCION_ADMIN, None)
    context.user_data[SERVICIO] = servicio


def obtener_servicio(context):
    return context.user_data.get(SERVICIO)


def borrar_servicio(context):
    context.user_data.pop(SERVICIO, None)


def guardar_accion_admin(context, accion):
    context.user_data.pop(SERVICIO, None)
    context.user_data[ACCION_ADMIN] = accion


def obtener_accion_admin(context):
    return context.user_data.get(ACCION_ADMIN)


def borrar_accion_admin(context):
    context.user_data.pop(ACCION_ADMIN, None)


def borrar_todo(context):
    borrar_servicio(context)
    borrar_accion_admin(context)
