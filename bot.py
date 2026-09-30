"""
TRENT — Bot de bienvenida / redirección al canal de Telegram
================================================================

CONTEXTO
--------
Este bot existe para esquivar un problema con Telegram Ads: al intentar
promocionar directamente el canal público @trentthacoo, la plataforma de
anuncios de Telegram (ads.telegram.org) devuelve el error
"Only public channels, bots and users allowed" incluso siendo el canal
100% público con 41K+ miembros. Como los BOTS sí están permitidos como
destino de un anuncio, este bot actúa de "puerta de entrada":

    Usuario hace clic en el anuncio de Telegram Ads
      -> Se abre el chat con este bot
      -> Telegram muestra automáticamente el botón "START" (nativo,
         el usuario NO escribe nada)
      -> El usuario toca "START" -> Telegram manda /start solo
      -> Este bot responde al instante con un mensaje + botón
         "Unirme al canal" que lleva directo a t.me/trentthacoo

Es el flujo con menos fricción posible dentro de las reglas de Telegram
(no se puede unir a alguien a un canal con cero clicks, es una
restricción de la propia plataforma, no de este bot).

CONFIGURACIÓN
--------------
El token del bot se lee de la variable de entorno TELEGRAM_BOT_TOKEN.
NO lo pongas escrito directamente en este archivo si vas a subirlo a un
repo público — configúralo como variable de entorno en Railway
(Settings -> Variables -> TELEGRAM_BOT_TOKEN).

Para probarlo en local:
    export TELEGRAM_BOT_TOKEN="8969716112:AAFoW12zRYwLS3QdL-Eg_jmP3MuyAURtIBI"
    python bot.py

DEPENDENCIAS
------------
pip install python-telegram-bot==21.*
(ver requirements.txt incluido)
"""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ---------------------------------------------------------------------------
# CONFIG — edita aquí lo que quieras cambiar sin tocar el resto del código
# ---------------------------------------------------------------------------

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")

CHANNEL_URL = "https://t.me/trentthacoo"
CHANNEL_BUTTON_TEXT = "🔥 Unirme al canal"

# Ruta del logo que se manda junto con el mensaje de bienvenida.
# Tiene que estar en la misma carpeta que este script (o pon la ruta
# completa si lo tienes en otro sitio).
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.jpg")

WELCOME_MESSAGE = (
    "¡Bienvenido a TRENT! 👟\n\n"
    "Únete a nuestro canal para ver todos los descuentos y ofertas "
    "de Hacoo con el código *TRENT14* (-14%)\n\n"
    "👇 Pulsa aquí para entrar"
)

# ---------------------------------------------------------------------------
# LOGGING
# ---------------------------------------------------------------------------

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# HANDLERS
# ---------------------------------------------------------------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Se dispara automáticamente cuando alguien abre el bot por primera vez
    y toca el botón "START" que Telegram muestra solo (o si escribe /start
    a mano, también funciona igual). No hace falta que el usuario escriba
    nada más.
    """
    user = update.effective_user
    logger.info("Nuevo /start de user_id=%s username=%s", user.id, user.username)

    keyboard = [[InlineKeyboardButton(CHANNEL_BUTTON_TEXT, url=CHANNEL_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if os.path.exists(LOGO_PATH):
        with open(LOGO_PATH, "rb") as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=WELCOME_MESSAGE,
                reply_markup=reply_markup,
                parse_mode="Markdown",
            )
    else:
        # Si no encuentra el logo, no rompe el bot: manda solo el texto.
        logger.warning("No se encontró el logo en %s, mando solo texto.", LOGO_PATH)
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /help por si alguien lo escribe, opcional pero útil."""
    keyboard = [[InlineKeyboardButton(CHANNEL_BUTTON_TEXT, url=CHANNEL_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Este bot te lleva directo a nuestro canal de ofertas TRENT x Hacoo.",
        reply_markup=reply_markup,
    )


async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Cualquier otro mensaje que escriba el usuario (texto suelto, stickers,
    etc.) le vuelve a mostrar el botón del canal, por si se ha perdido.
    """
    keyboard = [[InlineKeyboardButton(CHANNEL_BUTTON_TEXT, url=CHANNEL_URL)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "👇 Aquí tienes el acceso a nuestro canal:",
        reply_markup=reply_markup,
    )


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError(
            "Falta el token del bot. Define la variable de entorno "
            "TELEGRAM_BOT_TOKEN antes de arrancar el bot."
        )

    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    from telegram.ext import MessageHandler, filters
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, fallback))

    logger.info("Bot arrancado. Esperando mensajes...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
