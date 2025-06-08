import os
import logging
import asyncpg
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONFIGURAZIONE AMBIENTE ---
MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 8080))  # Fallback a 8080 se PORT non è settata
WEBHOOK_PATH = f"/webhook/{MAIN_BOT_TOKEN}"

if not MAIN_BOT_TOKEN or not DATABASE_URL:
    logger.error("MAIN_BOT_TOKEN o DATABASE_URL non settate!")
    exit(1)

# --- TELEGRAM BOT SETUP ---
bot = Bot(token=MAIN_BOT_TOKEN)
application = Application.builder().bot(bot).build()

# --- DATABASE ---
async def init_db():
    return await asyncpg.create_pool(DATABASE_URL)

db_pool = None

# --- COMANDI ---
async def collega_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Uso corretto: /collegaCanali <id_canale_sorgente> <id_canale_destinazione>")
        return
    source, dest = context.args
    async with db_pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_channels(user_id, source_channel_id, destination_channel_id)
            VALUES($1, $2, $3)
            ON CONFLICT (user_id)
            DO UPDATE SET source_channel_id = EXCLUDED.source_channel_id,
                          destination_channel_id = EXCLUDED.destination_channel_id
            """,
            update.effective_user.id, int(source), int(dest)
        )
    await update.message.reply_text(f"Canali collegati: {source} -> {dest}")

async def mostra_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT source_channel_id, destination_channel_id FROM user_channels WHERE user_id = $1",
            update.effective_user.id
        )
    if row:
        await update.message.reply_text(
            f"Hai collegato Canale Sorgente: {row['source_channel_id']} con Canale Destinazione: {row['destination_channel_id']}"
        )
    else:
        await update.message.reply_text("Non hai ancora collegato nessun canale.")

# --- WEBHOOK ---
async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.update_queue.put(update)
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Errore webhook: {e}")
        return web.Response(status=500)

# --- AVVIO ---
async def on_startup(app):
    global db_pool
    db_pool = await init_db()
    logger.info("Database connesso")

application.add_handler(CommandHandler("collegaCanali", collega_canali))
application.add_handler(CommandHandler("mostraCanali", mostra_canali))

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.on_startup.append(on_startup)

logger.info(f"Avvio bot con webhook {WEBHOOK_PATH} sulla porta {PORT}")

if __name__ == "__main__":
    web.run_app(app, port=PORT)
