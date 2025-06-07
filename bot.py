import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
import asyncio

BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))
PORT = int(os.getenv("PORT", "10000"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://tuo-bot.onrender.com

logging.basicConfig(level=logging.INFO)

async def forward_filtered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.text:
        text = update.channel_post.text
        if "rating" in text.lower():
            await context.bot.forward_message(
                chat_id=TARGET_CHANNEL_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_id=update.channel_post.message_id
            )

async def run():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(
        filters.Chat(SOURCE_CHANNEL_ID) & filters.TEXT,
        forward_filtered
    ))

    await app.initialize()
    await app.bot.set_webhook(WEBHOOK_URL)
    await app.start()
    await app.updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="",
        webhook_url=WEBHOOK_URL
    )

    # non chiudere il loop: resta attivo
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.get_event_loop().run_until_complete(run())
    except Exception as e:
        logging.exception("Errore durante l'avvio del bot:", exc_info=e)
