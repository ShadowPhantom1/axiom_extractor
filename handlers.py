from aiogram import Router, F, Bot
from aiogram.types import Message
from config import TRIGGER_CMD

router = Router()

# ============================================================
# MEDIA CACHE — Yeh sabse important part hai
# Jab koi bhi message aata hai Chat Automation se, uska media
# file_id yahan store ho jaata hai. View-once media bhi pehli
# baar aane par yahan cache ho jaata hai. Baad me chahe
# Telegram us media ko delete kar de, humare paas file_id
# saved rehta hai aur hum usse bhej sakte hain.
# ============================================================
media_cache = {}


def _extract_media_info(msg: Message):
    """Message se media file_id aur type nikaalo."""
    if msg.photo:
        return msg.photo[-1].file_id, "photo"
    elif msg.video:
        return msg.video.file_id, "video"
    elif msg.animation:
        return msg.animation.file_id, "gif"
    elif msg.document:
        return msg.document.file_id, "document"
    elif msg.video_note:
        return msg.video_note.file_id, "video_note"
    elif msg.voice:
        return msg.voice.file_id, "voice"
    elif msg.sticker:
        return msg.sticker.file_id, "sticker"
    return None, None


# ============================================================
# STEP 1: Har incoming business message ka media cache karo
# Yeh handler SABSE PEHLE chalta hai — har message par.
# View-once ho ya normal, file_id yahan store ho jaata hai.
# ============================================================
@router.business_message()
async def cache_all_media(message: Message):
    """Har aane wale message ka media silently cache karo."""
    file_id, media_type = _extract_media_info(message)

    if file_id:
        # Business connection chat_id + message_id se unique key banao
        cache_key = f"{message.business_connection_id}:{message.message_id}"
        media_cache[cache_key] = {
            "file_id": file_id,
            "type": media_type,
            "sender": message.from_user.id if message.from_user else "Unknown",
        }
        print(f"[📦] Cached {media_type} → msg {message.message_id}")


# ============================================================
# STEP 2: Trigger command detect karo aur media bhejo
# Jab user kisi message par reply karke .liketect likhe,
# toh cached file_id se media user ke bot chat me bhej do.
# ============================================================
@router.business_message(F.text == TRIGGER_CMD, F.reply_to_message)
async def on_trigger_extract(message: Message, bot: Bot):
    """Trigger reply detect karo → cached media bhejo."""

    owner_id = message.from_user.id
    target = message.reply_to_message
    target_id = target.message_id

    # Pehle cache me dekho (view-once media yahan se milega)
    cache_key = f"{message.business_connection_id}:{target_id}"
    cached = media_cache.get(cache_key)

    # Agar cache me hai toh cache se bhejo
    if cached:
        file_id = cached["file_id"]
        media_type = cached["type"]
        sender = cached["sender"]
        print(f"[⚡] Cache HIT! Extracting {media_type} from msg {target_id}")

    else:
        # Cache me nahi? Toh reply_to_message se try karo (normal media)
        file_id, media_type = _extract_media_info(target)
        sender = target.from_user.id if target.from_user else "Unknown"

        if not file_id:
            print(f"[x] No media found for msg {target_id} (not in cache, not in reply)")
            return

        print(f"[⚡] Cache MISS, using reply_to_message for {media_type}")

    caption = (
        f"📨 **Chat Automation Extract**\n"
        f"**Type:** `{media_type}`\n"
        f"**From:** `{sender}`"
    )

    try:
        if media_type == "photo":
            await bot.send_photo(chat_id=owner_id, photo=file_id, caption=caption)
        elif media_type == "video":
            await bot.send_video(chat_id=owner_id, video=file_id, caption=caption)
        elif media_type == "gif":
            await bot.send_animation(chat_id=owner_id, animation=file_id, caption=caption)
        elif media_type == "document":
            await bot.send_document(chat_id=owner_id, document=file_id, caption=caption)
        elif media_type == "video_note":
            await bot.send_video_note(chat_id=owner_id, video_note=file_id)
        elif media_type == "voice":
            await bot.send_voice(chat_id=owner_id, voice=file_id, caption=caption)
        elif media_type == "sticker":
            await bot.send_sticker(chat_id=owner_id, sticker=file_id)

        print(f"[✔] {media_type} → sent to user {owner_id}'s bot chat")

    except Exception as e:
        print(f"[✘] Send failed (user ne bot /start kiya hai?): {e}")
