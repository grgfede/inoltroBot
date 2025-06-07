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
    message = update.message or update.channel_post
    if not message:
        return

    chat_id = message.chat_id
    text = message.text or message.caption

    if chat_id == SOURCE_CHANNEL_ID and text and "rating" in text.lower():
        try:
            await bot.forward_message(
                chat_id=DEST_CHANNEL_ID,
                from_chat_id=chat_id,
                message_id=message.message_id
            )
            logger.info("Messaggio inoltrato")
        except Exception as e:
            logger.error(f"Errore inoltro: {e}")
    else:
        logger.info("Messaggio ignorato")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot attivo!")

async def on_startup(app):
    await application.initialize()  # ⚠️ IMPORTANTE!
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

# Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.ALL, forward_if_rating))

# Web server
app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
