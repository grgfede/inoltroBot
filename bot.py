import os
import logging
import asyncio
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH  # es. https://tuo-dominio.com/webhook/<TOKEN>

SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))  # canale da cui leggere
DEST_CHANNEL_ID = int(os.getenv("DEST_CHANNEL_ID"))      # canale dove inoltrare

async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Update ricevuto: {update}")

    text = None
    chat_id = None

    if update.message:
        chat_id = update.message.chat_id
        text = update.message.text or update.message.caption
    elif update.channel_post:
        chat_id = update.channel_post.chat_id
        text = update.channel_post.text or update.channel_post.caption

    logger.info(f"Messaggio da chat_id={chat_id} testo={text}")

    if chat_id == SOURCE_CHANNEL_ID and text:
        if "rating" in text.lower():
            try:
                await context.bot.send_message(chat_id=DEST_CHANNEL_ID, text=text)
                logger.info(f"Messaggio inoltrato al canale {DEST_CHANNEL_ID}")
            except Exception as e:
                logger.error(f"Errore durante inoltro: {e}")
        else:
            logger.info("Messaggio non contiene 'rating', nessun inoltro")
    else:
        logger.info(f"Messaggio da chat_id diverso da {SOURCE_CHANNEL_ID} o testo mancante, ignorato")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Comando /start ricevuto")
    await update.message.reply_text("Bot avviato!")

async def on_startup(application):
    bot = application.bot
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato a {WEBHOOK_URL}")

async def on_shutdown(application):
    bot = application.bot
    await bot.delete_webhook()
    logger.info("Webhook eliminato")

async def handle(request):
    try:
        data = await request.json()
        logger.info(f"Ricevuto update webhook: {data}")
        update = Update.de_json(data, bot)
        await application.process_update(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Errore nella gestione webhook: {e}")
        return web.Response(status=500)

if __name__ == "__main__":
    bot = Bot(token=TOKEN)
    application = ApplicationBuilder().bot(bot).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.ALL, forward_if_rating))

    async def main():
        await application.initialize()
        await application.start()

        app = web.Application()
        app.router.add_post(WEBHOOK_PATH, handle)

        app.on_startup.append(lambda app: on_startup(application))
        app.on_cleanup.append(lambda app: on_shutdown(application))

        logger.info("Avvio bot con webhook")
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", int(os.getenv("PORT", 8080)))
        await site.start()

        # loop infinito per tenere in vita il server
        while True:
            await asyncio.sleep(3600)

    asyncio.run(main())
