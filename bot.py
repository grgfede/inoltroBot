from telegram import Bot
import asyncio

async def delete_webhook():
    bot = Bot(token=os.getenv("BOT_TOKEN"))
    await bot.delete_webhook()
    print("Webhook eliminato.")

asyncio.run(delete_webhook())
