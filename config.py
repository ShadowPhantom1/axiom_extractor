import os

# === Render Environment Variables se config load hoga ===
# Render Dashboard → Environment me yeh set karo:
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Reply trigger command (optional: environment variable se bhi le sakte hain)
TRIGGER_CMD = os.environ.get("TRIGGER_CMD", ".liketect")
