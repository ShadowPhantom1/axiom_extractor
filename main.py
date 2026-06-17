import asyncio
import sys
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, TRIGGER_CMD
from handlers import router

# === Dummy Web Server for Render ===
async def handle_ping(request):
    return web.Response(text="Axiom Bot is running perfectly!")

async def start_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render assigns a port dynamically via the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f"[✔] Dummy Web Server running on port {port} (To keep Render happy)")

# === Bot Startup ===
async def boot():
    print("=" * 50)
    print("  📨 AXIOM — Chat Automation Bot")
    print("  🚀 Hosted on Render (Web Service)")
    print("=" * 50)

    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[✘] BOT_TOKEN environment variable set nahi hai!")
        print("[!] Render Dashboard → Environment → BOT_TOKEN add karo.")
        sys.exit(1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    print(f"[✔] Bot is LIVE! Trigger: {TRIGGER_CMD}")
    print("[*] Bot ko add karo: Settings → Account → Chat Automation")
    print("[*] Pehle bot ko /start karo apne DM me!\n")

    # Start the dummy server in the background
    await start_dummy_server()

    # Start the bot
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(boot())
