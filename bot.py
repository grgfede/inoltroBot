import os
import logging
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
import asyncpg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variabili d'ambiente
MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{MAIN_BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH

DATABASE_URL = os.getenv("DATABASE_URL")  # es: postgres://user:pass@host/dbname

# Costruzione bot e application
bot = Bot(token=MAIN_BOT_TOKEN)
application = ApplicationBuilder().bot(bot).build()

# Connessione a DB
async def create_db_pool():
    return await asyncpg.create_pool(DATABASE_URL)

db_pool = None

# Comando /collegaCanali: salva associazione canale utente
async def collega_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Uso: /collegaCanali <SOURCE_CHANNEL_ID> <DEST_CHANNEL_ID>")
        return

    source_id, dest_id = args
    try:
        source_id = int(source_id)
        dest_id = int(dest_id)
    except ValueError:
        await update.message.reply_text("Gli ID dei canali devono essere numeri interi.")
        return

    async with db_pool.acquire() as conn:
        await conn.execute(
            "INSERT INTO user_channels(user_id, source_channel_id, dest_channel_id) "
            "VALUES($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET source_channel_id = $2, dest_channel_id = $3",
            user_id, source_id, dest_id
        )

    await update.message.reply_text(f"Hai collegato il canale {source_id} con {dest_id}.")

# Comando /mostraCanali: mostra canali collegati all'utente
async def mostra_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT source_channel_id, dest_channel_id FROM user_channels WHERE user_id = $1",
            user_id
        )
    if row:
        await update.message.reply_text(
            f"Hai collegato Canale A: {row['source_channel_id']} con Canale B: {row['dest_channel_id']}"
        )
    else:
        await update.message.reply_text("Non hai ancora collegato nessun canale.")

# Forward solo se il messaggio è da un canale collegato dall'utente e contiene 'rating'
async def forward_if_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    if not (chat_id and text and message_id):
        return

    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT dest_channel_id FROM user_channels WHERE source_channel_id = $1",
            chat_id
        )

    if rows and "rating" in text.lower():
        for row in rows:
            try:
                await context.bot.forward_message(
                    chat_id=row["dest_channel_id"],
                    from_chat_id=chat_id,
                    message_id=message_id,
                )
                logger.info(f"Inoltrato messaggio {message_id} da {chat_id} a {row['dest_channel_id']}")
            except Exception as e:
                logger.error(f"Errore inoltro messaggio: {e}")

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Benvenuto! Usa /collegaCanali <ID_CANALE_SORGENTE> <ID_CANALE_DESTINAZIONE> per collegare i canali.\n"
        "Usa /mostraCanali per vedere i canali collegati."
    )

# Healthcheck per uptime robot
async def healthcheck(request):
    return web.Response(text="Bot online!", status=200)

# Gestione webhook
async def handle(request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.update_queue.put(update)
        return web.Response()
    except Exception as e:
        logger.error(f"Errore gestione webhook: {e}")
        return web.Response(status=500)

async def on_startup(app):
    global db_pool
    db_pool = await create_db_pool()
    await bot.set_webhook(WEBHOOK_URL)
    logger.info(f"Webhook impostato su {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    logger.info("Webhook eliminato")
    await db_pool.close()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("collegaCanali", collega_canali))
    application.add_handler(CommandHandler("mostraCanali", mostra_canali))
    application.add_handler(MessageHandler(filters.ALL, forward_if_rating))

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle)
    app.router.add_get("/", healthcheck)

    app.on_startup.append(lambda app: on_startup(application))
    app.on_cleanup.append(lambda app: on_shutdown(application))

    logger.info(f"Avvio bot con webhook {WEBHOOK_PATH} sulla porta {port}")
    web.run_app(app, port=port)
