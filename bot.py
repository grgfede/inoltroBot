import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://tuo-dominio.com + WEBHOOK_PATH
PORT = int(os.getenv("PORT", "8443"))

async def forward_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("✅ Ricevuto messaggio!")
    text = update.message.text
    # Se nel testo c'è "rating" in qualsiasi maiuscola/minuscola
    if text and ("rating" in text.lower()):
        # Inoltra il messaggio su canale B (ID canale da env var)
        dest_channel_id = int(os.getenv("DEST_CHANNEL_ID"))
        await context.bot.send_message(chat_id=dest_channel_id, text=text)

async def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), forward_messages))

    # Avvia il webhook server integrato aiohttp
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL + WEBHOOK_PATH,
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
