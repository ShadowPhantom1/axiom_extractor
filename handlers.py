from aiogram import Router, Bot
from aiogram.types import Message, BusinessConnection
from aiogram.filters import CommandStart
from config import TRIGGER_CMD

router = Router()

# ============================================================
# MEDIA CACHE — Jab media message pehli baar aata hai tab
# uska file_id yahan store hota hai
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


async def _send_media(bot: Bot, chat_id: int, file_id: str, media_type: str, caption: str):
    """Media type ke hisaab se bhejo."""
    if media_type == "photo":
        await bot.send_photo(chat_id=chat_id, photo=file_id, caption=caption)
    elif media_type == "video":
        await bot.send_video(chat_id=chat_id, video=file_id, caption=caption)
    elif media_type == "gif":
        await bot.send_animation(chat_id=chat_id, animation=file_id, caption=caption)
    elif media_type == "document":
        await bot.send_document(chat_id=chat_id, document=file_id, caption=caption)
    elif media_type == "video_note":
        await bot.send_video_note(chat_id=chat_id, video_note=file_id)
    elif media_type == "voice":
        await bot.send_voice(chat_id=chat_id, voice=file_id, caption=caption)
    elif media_type == "sticker":
        await bot.send_sticker(chat_id=chat_id, sticker=file_id)


# ============================================================
# /start COMMAND — Bot ke DM me /start karne par response
# ============================================================
@router.message(CommandStart())
async def cmd_start(message: Message):
    print(f"[✔] /start received from user {message.from_user.id}")
    await message.answer(
        "✅ **Axiom Chat Automation Bot is Active!**\n\n"
        f"🔹 Trigger Command: `{TRIGGER_CMD}`\n"
        "🔹 Kisi bhi chat me media par reply karke trigger likho\n"
        "🔹 Media yahan DM me aa jayega!\n\n"
        "⚠️ Bot ko Chat Automation me add karna mat bhulna:\n"
        "Settings → Account → Chat Automation",
        parse_mode="Markdown"
    )


# ============================================================
# BUSINESS CONNECTION — Jab bot Chat Automation me add/remove ho
# ============================================================
@router.business_connection()
async def on_business_connection(event: BusinessConnection):
    user = event.user
    enabled = event.is_enabled
    status = "CONNECTED" if enabled else "DISCONNECTED"
    print(f"[🔗] Business {status} | User: {user.first_name} (ID: {user.id})")


# ============================================================
# BUSINESS MESSAGE — Har chat message yahan aata hai
# Step 1: Media cache karo
# Step 2: Agar trigger reply hai toh media DM me bhejo
# ============================================================
@router.business_message()
async def handle_business_message(message: Message, bot: Bot):
    print(f"[📩] Business msg received | chat={message.chat.id} | from={message.from_user.id if message.from_user else '?'} | text={message.text or '[media/other]'}")

    # --- STEP 1: Media Cache ---
    file_id, media_type = _extract_media_info(message)
    if file_id:
        cache_key = f"{message.chat.id}:{message.message_id}"
        media_cache[cache_key] = {
            "file_id": file_id,
            "type": media_type,
            "sender": message.from_user.id if message.from_user else "Unknown",
        }
        print(f"[📦] Cached {media_type} | chat={message.chat.id} msg={message.message_id} | cache size={len(media_cache)}")

    # --- STEP 2: Trigger Check ---
    if message.text and message.text.strip() == TRIGGER_CMD and message.reply_to_message:
        owner_id = message.from_user.id
        target = message.reply_to_message
        target_id = target.message_id

        print(f"[⚡] TRIGGER DETECTED! owner={owner_id} | target_msg={target_id}")

        # Pehle cache me dekho
        cache_key = f"{message.chat.id}:{target_id}"
        cached = media_cache.get(cache_key)

        if cached:
            t_file_id = cached["file_id"]
            t_media_type = cached["type"]
            t_sender = cached["sender"]
            print(f"[⚡] Cache HIT! {t_media_type}")
        else:
            # Cache miss — reply_to_message se try karo
            t_file_id, t_media_type = _extract_media_info(target)
            t_sender = target.from_user.id if target.from_user else "Unknown"

            if not t_file_id:
                print(f"[✘] NO MEDIA FOUND for msg {target_id} (not in cache, not in reply)")
                return

            print(f"[⚡] Cache MISS, using reply_to_message | {t_media_type}")

        caption = (
            f"📨 **Chat Automation Extract**\n"
            f"**Type:** `{t_media_type}`\n"
            f"**From:** `{t_sender}`"
        )

        try:
            await _send_media(bot, owner_id, t_file_id, t_media_type, caption)
            print(f"[✔] SUCCESS! {t_media_type} → sent to user {owner_id}")
        except Exception as e:
            print(f"[✘] SEND FAILED: {e}")
            print(f"[!] Kya user {owner_id} ne bot ko /start kiya hai?")
