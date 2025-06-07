import os
import logging
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH  # es. https://tuo-dominio.com/webhook/<TOKEN>

SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))  # canale da cui leggere
DEST_CHANNEL_ID = int(os.getenv("DEST_CHANNEL_ID"))      # canale dove inoltrare

async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Usare channel_post per messaggi canale
    post = update.channel_post
    if post and post.chat_id == SOURCE_CHANNEL_ID:
        text = post.text or post.caption or ""
        logger.info(f"Messaggio ricevuto da canale_id={post.chat_id} testo={text}")

        if "rating" in text.lower():
            try:
                await context.bot.send_message(chat_id=DEST_CHANNEL_ID, text=text)
                logger.info(f"Messaggio inoltrato al canale {DEST_CHANNEL_ID}")
            except Exception as e:
                logger.error(f"Errore durante inoltro: {e}")
        else:
            logger.info("Messaggio non contiene 'rating', nessun inoltro")
    else:
        logger.info(f"Messaggio non da canale {SOURCE_CHANNEL_ID}, ignorato")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Comando /start ricevuto")
    await update.message.reply_text("Bot avviato!")

async def on_startup(app):
    bot = app.bot
    # Imposta il webhook
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato a {WEBHOOK_URL}")

async def on_shutdown(app):
    bot = app.bot
    await bot.delete_webhook()
    logger.info("Webhook eliminato")

async def handle(request):
    """Handler aiohttp per la ricezione delle richieste webhook Telegram"""
    try:
        data = await request.json()
        logger.info(f"Ricevuto update webhook: {data}")
        update = Update.de_json(data, bot)
        await application.update_queue.put(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Errore nella gestione webhook: {e}")
        return web.Response(status=500)

if __name__ == "__main__":
    # Crea bot e application
    bot = Bot(token=TOKEN)
    application = ApplicationBuilder().bot(bot).build()

    # Aggiungi handler:
    application.add_handler(CommandHandler("start", start))
    # Nota: usa filters.Chat e filters.ALL perché il messaggio vero arriva come channel_post
    application.add_handler(MessageHandler(filters.ALL & filters.Chat(chat_id=SOURCE_CHANNEL_ID), forward_if_rating))

    # Server aiohttp per ricevere webhook
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)

    # Eventi startup/shutdown webhook
    app.on_startup.append(lambda app: on_startup(application))
    app.on_cleanup.append(lambda app: on_shutdown(application))

    logger.info("Avvio bot con webhook")
    # Avvia tutto
    web.run_app(app, port=int(os.getenv("PORT", 8080)))
