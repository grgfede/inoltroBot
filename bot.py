import os
import logging
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
DEST_CHANNEL_ID = int(os.getenv("DEST_CHANNEL_ID"))

# Initialize bot and app
bot = Bot(token=TOKEN)
application = ApplicationBuilder().bot(bot).build()

# Handler to forward messages that contain 'rating'
async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"[Messaggio ricevuto] Update: {update}")

    text = None
    chat_id = None
    message_id = None

    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text or update.message.caption
        message_id = update.message.message_id
    elif update.channel_post:
        chat_id = update.channel_post.chat_id
        text = update.channel_post.text or update.channel_post.caption
        message_id = update.channel_post.message_id

    logger.info(f"Messaggio da chat_id={chat_id} testo={text} message_id={message_id}")

    if chat_id == SOURCE_CHANNEL_ID and text:
        # Primo test: invio messaggio di prova nel canale di destinazione
        try:
            logger.info(f"Invio messaggio di test nel canale {DEST_CHANNEL_ID}")
            await context.bot.send_message(chat_id=DEST_CHANNEL_ID, text="Messaggio di test dal bot")
        except Exception as e:
            logger.error(f"Errore durante invio messaggio di test: {e}", exc_info=True)

        # Se il messaggio contiene 'rating', inoltra
        if "rating" in text.lower():
            try:
                logger.info(f"Forwarding message from chat {chat_id} with message_id {message_id}")
                await context.bot.forward_message(
                    chat_id=DEST_CHANNEL_ID,
                    from_chat_id=SOURCE_CHANNEL_ID,
                    message_id=message_id
                )
                logger.info("Messaggio inoltrato con successo")
            except Exception as e:
                logger.error(f"Errore durante inoltro: {e}", exc_info=True)
        else:
            logger.info("Messaggio ignorato (non contiene 'rating')")
    else:
        logger.info("Messaggio ignorato (provenienza chat differente o testo assente)")

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot avviato!")

# Healthcheck endpoint (ping da UptimeRobot)
async def healthcheck(request):
    return web.Response(text="Bot online!", status=200)

# Webhook handler
async def handle(request):
    try:
        data = await request.json()
        logger.info(f"[Webhook ricevuto] {data}")

        update = Update.de_json(data, bot)
        await application.initialize()  # Necessario per usare update_queue
        await application.update_queue.put(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Errore nella gestione webhook: {e}", exc_info=True)
        return web.Response(status=500)

# Startup webhook setup
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato a {WEBHOOK_URL}")

# Shutdown cleanup
async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("Webhook eliminato")

# Main app
if __name__ == "__main__":
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, forward_if_rating))

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.router.add_get("/", healthcheck)  # Per UptimeRobot

    app.on_startup.append(lambda app: on_startup(application))
    app.on_cleanup.append(lambda app: on_shutdown(application))

    logger.info("Avvio bot con webhook")
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
