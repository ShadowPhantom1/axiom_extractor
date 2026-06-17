import asyncio
import sys
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, TRIGGER_CMD
from handlers import router


async def handle_ping(request):
    return web.Response(text="Axiom Bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[✔] Web Server on port {port}")


async def boot():
    print("=" * 50)
    print("  📨 AXIOM — Chat Automation Bot")
    print("=" * 50)

    if not BOT_TOKEN:
        print("[✘] BOT_TOKEN not set! Add it in Render Environment.")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await start_web_server()

    print(f"[✔] Bot LIVE! Trigger: {TRIGGER_CMD}")
    print("[*] Listening for business_message updates...\n")

    # IMPORTANT: Explicitly include business updates
    await dp.start_polling(
        bot,
        allowed_updates=[
            "message",
            "business_connection",
            "business_message",
            "edited_business_message",
            "deleted_business_messages",
        ]
    )


if __name__ == "__main__":
    asyncio.run(boot())
