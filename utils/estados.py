# Estados temporales de usuarios
# Guarda qué acción está esperando el bot de cada usuario


estados_usuarios = {}


def guardar_estado(user_id, estado):
    """
    Guarda el estado actual del usuario.
    
    Ejemplo:
    user_id = 123456
    estado = "DISNEY"
    """

    estados_usuarios[user_id] = estado


def obtener_estado(user_id):
    """
    Obtiene el estado actual del usuario.
    """

    return estados_usuarios.get(user_id)


def borrar_estado(user_id):
    """
    Elimina el estado cuando termina la consulta.
    """

    if user_id in estados_usuarios:
        del estados_usuarios[user_id]