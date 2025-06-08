import os
from aiohttp import web
import asyncio

PORT = int(os.getenv("PORT", 8080))

async def ping(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get("/ping", ping)

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print(f"Server running on port {PORT}")
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
