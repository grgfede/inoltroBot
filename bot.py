import os
import logging
import asyncpg
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

# Variabili ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH
PORT = int(os.getenv("PORT", 8080))
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=BOT_TOKEN)
application = ApplicationBuilder().bot(bot).build()

# Pool DB globale
db_pool = None


async def init_db_pool():
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    # Crea tabella se non esiste
    async with db_pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS user_channels (
                user_id BIGINT,
                source_channel_id TEXT,
                dest_channel_id TEXT,
                PRIMARY KEY(user_id, source_channel_id)
            )
        """)


# Comando /collegaCanali <source_channel_id> <dest_channel_id>
async def collega_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Uso corretto:\n/collegaCanali <source_channel_id> <dest_channel_id>")
        return

    source_channel_id = args[0]
    dest_channel_id = args[1]

    async with db_pool.acquire() as conn:
        await conn.execute("""
            INSERT INTO user_channels(user_id, source_channel_id, dest_channel_id)
            VALUES($1, $2, $3)
            ON CONFLICT (user_id, source_channel_id)
            DO UPDATE SET dest_channel_id = EXCLUDED.dest_channel_id
        """, user_id, source_channel_id, dest_channel_id)

    await update.message.reply_text(f"✅ Collegato il canale sorgente {source_channel_id} al canale destinazione {dest_channel_id}")


# Comando /mostraCanali
async def mostra_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT source_channel_id, dest_channel_id FROM user_channels WHERE user_id = $1",
            user_id
        )

    if not rows:
        await update.message.reply_text("Non hai ancora collegato canali.")
        return

    msg = "Ecco i canali che hai collegato:\n\n"
    for row in rows:
        msg += f"Canale sorgente: {row['source_channel_id']} ➡️ Canale destinazione: {row['dest_channel_id']}\n"

    await update.message.reply_text(msg)


# Funzione che inoltra messaggi contenenti "rating"
async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = None
    chat_id = None
    message_id = None

    if update.message:
        chat_id = str(update.message.chat_id)
        text = update.message.text or update.message.caption
        message_id = update.message.message_id
    elif update.channel_post:
        chat_id = str(update.channel_post.chat_id)
        text = update.channel_post.text or update.channel_post.caption
        message_id = update.channel_post.message_id
    else:
        return

    if not (chat_id and text and message_id):
        return

    if "rating" not in text.lower():
        return

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT dest_channel_id FROM user_channels WHERE source_channel_id = $1",
            chat_id
        )

    if not rows:
        logger.info(f"Nessuna configurazione di inoltro per canale {chat_id}")
        return

    for row in rows:
        dest_channel_id = int(row['dest_channel_id'])
        try:
            logger.info(f"Inoltro messaggio {message_id} da {chat_id} a {dest_channel_id}")
            await context.bot.forward_message(
                chat_id=dest_channel_id,
                from_chat_id=int(chat_id),
                message_id=message_id
            )
            logger.info("Inoltro effettuato con successo")
        except Exception as e:
            logger.error(f"Errore inoltro a {dest_channel_id}: {e}")


# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Ciao! Sono il bot per inoltrare messaggi contenenti 'rating'.\n\n"
        "Usa /collegaCanali <source_channel_id> <dest_channel_id> per collegare i canali.\n"
        "Usa /mostraCanali per vedere le tue configurazioni."
    )


# Healthcheck endpoint per UptimeRobot o simili
async def healthcheck(request):
    return web.Response(text="Bot online!", status=200)


# Webhook handler aiohttp
async def handle(request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.update_queue.put(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Errore gestione webhook: {e}")
        return web.Response(status=500)


# Startup webhook setup
async def on_startup(app):
    await init_db_pool()
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato a {WEBHOOK_URL}")


# Shutdown cleanup
async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("Webhook eliminato")
    if db_pool:
        await db_pool.close()


if __name__ == "__main__":
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("collegaCanali", collega_canali))
    application.add_handler(CommandHandler("mostraCanali", mostra_canali))
    application.add_handler(MessageHandler(filters.ALL, forward_if_rating))

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.router.add_get("/", healthcheck)

    app.on_startup.append(lambda app: on_startup(application))
    app.on_cleanup.append(lambda app: on_shutdown(application))

    logger.info("Avvio bot con webhook")
    web.run_app(app, port=PORT)
