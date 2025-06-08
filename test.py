from aiohttp import web

async def handle(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get("/", handle)

if __name__ == "__main__":
    print("Starting app on port 8080")
    web.run_app(app, port=8080)
