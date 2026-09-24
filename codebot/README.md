# Codebot – Bot de códigos de streaming (Refills EC)

Bot de Telegram que lee el Gmail de la cuenta y entrega a cada cliente
el código de Disney+ / Amazon Prime o el link de acceso temporal de Netflix,
solo para los correos que tiene autorizados.

## 1. Antes de subirlo (IMPORTANTE)

Las claves de la versión anterior estaban escritas en el código, así que hay que cambiarlas:

1. **Gmail**: myaccount.google.com → Seguridad → Contraseñas de aplicaciones → borra la vieja y crea una nueva.
2. **Telegram**: en @BotFather → `/revoke` → elige el bot → copia el token nuevo.
3. **MongoDB Atlas**: Database Access → edita `refillsec_db_user` → nueva contraseña.

Si el repositorio estuvo en GitHub, borra también el historial o crea un repo nuevo,
porque las claves viejas siguen en los commits anteriores.

## 2. Configuración

- **En tu PC**: copia `.env.example` como `.env` y llena los datos nuevos.
- **En el hosting (Render u otro)**: agrega las mismas variables en el panel
  "Environment": `EMAIL_USER`, `EMAIL_PASS`, `TOKEN_TELEGRAM`, `MONGO_URI`, `ADMIN_ID`.
  Opcionales: `DATABASE_NAME` (por defecto `bot_gestion`), `MINUTOS_VALIDEZ` (por defecto `20`).
- Para tener varios administradores: `ADMIN_ID=111111,222222`.

Instalar y correr:

    pip install -r requirements.txt
    python app.py

## 3. Uso del panel admin

- **Registrar / agregar correos**: `ID|correo1@gmail.com, correo2@gmail.com`
  (si el usuario ya existe, se suman los correos). `ID|*` da acceso a todo.
- **Quitar un correo**: `ID|correo@gmail.com`
- **Eliminar usuario**: solo el ID.
- `/cancelar` sale de cualquier operación.

El cliente puede ver su ID de Telegram en "Mis cuentas" si aún no está registrado.

## 4. Notas

- Al arrancar, el bot repara automáticamente los usuarios guardados con la
  versión anterior (correos guardados como texto y registros duplicados).
- Solo se entregan códigos/links que llegaron en los últimos `MINUTOS_VALIDEZ` minutos.
- El bot solo responde en chats privados.
