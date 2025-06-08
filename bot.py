import os
import logging
import asyncpg
from aiohttp import web
from telegram import Update, Bot
from telegram.ext import (
    Application, CommandHandler, ContextTypes
)
import asyncio
import httpx

# --- LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- ENV VARS ---
MAIN_BOT_TOKEN = os.getenv("MAIN_BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://tuobot.onrender.com
WEBHOOK_PATH = f"/webhook/{MAIN_BOT_TOKEN}"
DATABASE_URL = os.getenv("DATABASE_URL")
PORT = int(os.getenv("PORT", 8080))

logger.info(f"WEBHOOK_URL: {WEBHOOK_URL}")

# --- CHECK ---
if not MAIN_BOT_TOKEN or not DATABASE_URL or not WEBHOOK_URL:
    logger.error("MAIN_BOT_TOKEN, DATABASE_URL o WEBHOOK_URL non settati!")
    exit(1)

# --- BOT E APP ---
bot = Bot(token=MAIN_BOT_TOKEN)
application = Application.builder().bot(bot).build()

# --- DB INIT ---
async def init_db():
    return await asyncpg.create_pool(DATABASE_URL)

db_pool = None

# --- HEALTH CHECK /ping ---
async def ping(request):
    return web.Response(text="OK")

# --- COMANDI ---
async def collega_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Comando /collegaCanali ricevuto da {update.effective_user.id} con args: {context.args}")
    if len(context.args) != 2:
        await update.message.reply_text("Uso corretto: /collegaCanali <id_sorgente> <id_destinazione>")
        return
    source, dest = context.args
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO user_channels(user_id, source_channel_id, destination_channel_id) VALUES($1, $2, $3) "
                "ON CONFLICT (user_id) DO UPDATE SET source_channel_id = EXCLUDED.source_channel_id, "
                "destination_channel_id = EXCLUDED.destination_channel_id",
                update.effective_user.id, int(source), int(dest)
            )
        await update.message.reply_text(f"Canali collegati: {source} -> {dest}")
        logger.info(f"Salvato collegamento canali per utente {update.effective_user.id}")
    except Exception as e:
        logger.error(f"Errore nel comando collegaCanali: {e}")
        await update.message.reply_text("Si è verificato un errore durante il salvataggio.")

async def mostra_canali(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Comando /mostraCanali ricevuto da {update.effective_user.id}")
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT source_channel_id, destination_channel_id FROM user_channels WHERE user_id = $1",
                update.effective_user.id
            )
        if row:
            await update.message.reply_text(
                f"Hai collegato:\nCanale Sorgente: {row['source_channel_id']}\nCanale Destinazione: {row['destination_channel_id']}"
            )
        else:
            await update.message.reply_text("Non hai ancora collegato nessun canale.")
    except Exception as e:
        logger.error(f"Errore nel comando mostraCanali: {e}")
        await update.message.reply_text("Errore nel recuperare i canali.")

# --- HANDLER WEBHOOK ---
async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, bot)
        await application.update_queue.put(update)
        return web.Response(text="OK")
    except Exception as e:
        logger.error(f"Errore webhook: {e}")
        return web.Response(status=500)

# --- ATTENDI WEBHOOK DISPONIBILE ---
async def wait_for_webhook_ready(url, timeout=120):
    logger.info("Attendo che il dominio Render sia disponibile...")
    for _ in range(timeout):
        try:
            response = httpx.get(url)
            if response.status_code == 200:
                logger.info("Dominio Render disponibile")
                return True
        except Exception:
            pass
        await asyncio.sleep(2)
    logger.warning("Timeout nel raggiungere il dominio Render")
    return False

# --- STARTUP ---
async def on_startup():
    global db_pool
    db_pool = await init_db()
    logger.info("Database connesso")

    full_webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
    
    await wait_for_webhook_ready(f"{WEBHOOK_URL}/ping")

    current = await bot.get_webhook_info()
    if current.url != full_webhook_url:
        await bot.set_webhook(full_webhook_url)
        logger.info(f"Webhook registrato su Telegram: {full_webhook_url}")
    else:
        logger.info("Webhook già registrato correttamente")

# --- ROUTING E HANDLER ---
application.add_handler(CommandHandler("collegaCanali", collega_canali))
application.add_handler(CommandHandler("mostraCanali", mostra_canali))

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.router.add_get("/ping", ping)

logger.info(f"Avvio bot con webhook {WEBHOOK_URL}{WEBHOOK_PATH} sulla porta {PORT}")

async def main():
    await on_startup()

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()

    # Avvio l'app telegram in webhook mode senza passare web_app
    await application.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=WEBHOOK_PATH.lstrip("/"),
    )

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()
    asyncio.run(main())
