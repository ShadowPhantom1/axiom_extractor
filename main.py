import asyncio
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, TRIGGER_CMD
from handlers import router


async def boot():
    print("=" * 50)
    print("  📨 AXIOM — Chat Automation Bot")
    print("  🚀 Hosted on Render")
    print("=" * 50)

    # Startup me token check karo — Render pe crash mat ho silently
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

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(boot())
