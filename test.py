import os
from telegram import Bot
import asyncio

async def main():
    TOKEN = os.getenv("BOT_TOKEN")
    DEST_CHANNEL_ID = os.getenv("DEST_CHANNEL_ID")
    bot = Bot(token=TOKEN)

    # Test con ID numerico o username
    try:
        if DEST_CHANNEL_ID.startswith("@"):
            chat_id = DEST_CHANNEL_ID
        else:
            chat_id = int(DEST_CHANNEL_ID)

        await bot.send_message(chat_id=chat_id, text="✅ TEST: messaggio inviato dal bot!")
        print("Messaggio inviato con successo.")
    except Exception as e:
        print(f"❌ Errore durante invio messaggio: {e}")

asyncio.run(main())
