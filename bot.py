from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
TARGET_CHANNEL_ID = int(os.getenv("TARGET_CHANNEL_ID"))

async def forward_filtered(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.channel_post and update.channel_post.text:
        if "rating" in update.channel_post.text.lower():
            await context.bot.forward_message(
                chat_id=TARGET_CHANNEL_ID,
                from_chat_id=SOURCE_CHANNEL_ID,
                message_id=update.channel_post.message_id
            )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.Chat(SOURCE_CHANNEL_ID) & filters.TEXT, forward_filtered))
app.run_polling()
