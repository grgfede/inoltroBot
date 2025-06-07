import os
import logging
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH

SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
DEST_CHANNEL_ID = int(os.getenv("DEST_CHANNEL_ID"))

bot = Bot(token=TOKEN)
application = ApplicationBuilder().bot(bot).build()

async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Update ricevuto: {update}")

    message = update.message or update.channel_post
    if not message:
        logger.info("Nessun messaggio presente nell'update")
        return

    chat_id = message.chat_id
    text = message.text or message.caption

    logger.info(f"Messaggio ricevuto da chat_id={chat_id}, testo={text}")

    if chat_id == SOURCE_CHANNEL_ID and text and "rating" in text.lower():
        try:
            await bot.forward_message(
                chat_id=DEST_CHANNEL_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_id=message.message_id
            )
            logger.info("Messaggio inoltrato con successo")
        except Exception as e:
            logger.error(f"Errore inoltro: {e}")
    else:
        logger.info("Condizioni non soddisfatte per inoltro")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot attivo!")

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato a {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("Webhook eliminato")

async def handle(request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.update_queue.put(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Errore nel webhook handler: {e}")
        return web.Response(status=500)

# Aggiungi handler
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.ALL, forward_if_rating))

# App AIOHTTP
app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)
app.on_startup.append(lambda app: on_startup(application))
app.on_cleanup.append(lambda app: on_shutdown(application))

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
