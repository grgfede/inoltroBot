import os
import logging
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH  # es. https://tuo-dominio.com/webhook/<TOKEN>

SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))  # canale da cui leggere
DEST_CHANNEL_ID = int(os.getenv("DEST_CHANNEL_ID"))      # canale dove inoltrare

async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Controlla che il messaggio venga dal canale di origine
    if update.message and update.message.chat_id == SOURCE_CHANNEL_ID:
        text = update.message.text or ""
        if "rating" in text.lower():
            await context.bot.send_message(chat_id=DEST_CHANNEL_ID, text=text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot avviato!")

async def on_startup(app):
    bot = app.bot
    # Imposta il webhook
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook impostato a {WEBHOOK_URL}")

async def on_shutdown(app):
    bot = app.bot
    await bot.delete_webhook()
    logging.info("Webhook eliminato")

async def handle(request):
    """Handler aiohttp per la ricezione delle richieste webhook Telegram"""
    data = await request.json()
    update = Update.de_json(data, bot)
    await application.update_queue.put(update)
    return web.Response()

if __name__ == "__main__":
    # Crea bot e application
    bot = Bot(token=TOKEN)
    application = ApplicationBuilder().bot(bot).build()

    # Aggiungi handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.Chat(chat_id=SOURCE_CHANNEL_ID), forward_if_rating))

    # Server aiohttp per ricevere webhook
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)

    # Eventi startup/shutdown webhook
    app.on_startup.append(lambda app: on_startup(application))
    app.on_cleanup.append(lambda app: on_shutdown(application))

    # Avvia tutto
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
