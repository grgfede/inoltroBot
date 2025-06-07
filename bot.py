import os
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)
from http.server import BaseHTTPRequestHandler, HTTPServer
		 
import threading

# 🔐 Variabili ambiente
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))
PORT = int(os.getenv("PORT", "10000"))  # usato da Render
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # es: https://nome-app.onrender.com

logging.basicConfig(level=logging.INFO)

async def forward_filtered(update: Update, context: ContextTypes.DEFAULT_TYPE):
									
    if update.channel_post and update.channel_post.text:
        text = update.channel_post.text
        if any(word in text.lower() for word in ["rating"]):
            await context.bot.forward_message(
                chat_id=TARGET_CHANNEL_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_id=update.channel_post.message_id
            )

												   
																								 

# Web server per rispondere a webhook
class WebhookHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot online via webhook")

def start_webserver():
					  
												
						 
								   
							  
												
    server = HTTPServer(("", PORT), WebhookHandler)
    server.serve_forever()

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ⛓️ Handler messaggi canale
    app.add_handler(MessageHandler(
        filters.Chat(SOURCE_CHANNEL_ID) & filters.TEXT,
        forward_filtered
    ))

    # 🔗 Imposta webhook
    await app.bot.set_webhook(url=WEBHOOK_URL)
    await app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=WEBHOOK_URL
    )

# 👂 Avvia server HTTP in parallelo (opzionale per Render)
threading.Thread(target=start_webserver, daemon=True).start()

# 🚀 Avvio
import asyncio
asyncio.run(main())
