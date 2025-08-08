# sticker_bot_new_set_every_time.py
# Requirements:
#   pip install --upgrade python-telegram-bot pillow

import io
import time
from PIL import Image
from telegram import Update, InputSticker, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import os
TOKEN = os.getenv("TOKEN")


# ---------- helpers ----------
def to_webp_512(image_bytes: bytes) -> bytes:
    im = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    im.thumbnail((512, 512))  # keep aspect ratio; max side = 512
    out = io.BytesIO()
    im.save(out, format="WEBP")
    out.seek(0)
    return out.read()

def default_title(first_name: str | None) -> str:
    return f"{(first_name or 'Foydalanuvchi')} stiker to‘plami"

def unique_set_shortname(bot_username: str, user_id: int) -> str:
    # Add a timestamp so each set name is different
    ts = int(time.time())
    return f"uz_user_{user_id}_{ts}_by_{bot_username}".lower()


# ---------- handlers ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Rasm yuboring — men uni stikerga aylantirib beraman. 📷➡️🎟️"
    )

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    me = await context.bot.get_me()

    # Every time: generate a new name
    set_name = unique_set_shortname(me.username, user.id)
    set_title = default_title(user.first_name)

    # 1) download largest photo
    tfile = await update.message.photo[-1].get_file()
    original = await tfile.download_as_bytearray()

    # 2) convert to WEBP 512
    webp_bytes = to_webp_512(original)

    # 3) build InputSticker (emoji REQUIRED)
    input_sticker = InputSticker(sticker=io.BytesIO(webp_bytes), emoji_list=["🙂"])

    # 4) create a brand-new set every time
    try:
        await context.bot.create_new_sticker_set(
            user_id=user.id,
            name=set_name,
            title=set_title,
            stickers=[input_sticker],
            sticker_format="static",
        )
    except Exception as e_create:
        print("Create sticker set error:", e_create)
        await update.message.reply_text(
            "Kechirasiz, yangi stiker to‘plami yaratishda xatolik yuz berdi."
        )
        return

    # 5) send pack link
    pack_url = f"https://t.me/addstickers/{set_name}"
    kb = InlineKeyboardMarkup(
        [[InlineKeyboardButton("➕ stikerni qo‘shish", url=pack_url)]]
    )
    await update.message.reply_text(f"✅ Yangi stiker yaratildi: «{set_title}»", reply_markup=kb)

    # Optional: send sticker preview
    await update.message.reply_sticker(sticker=io.BytesIO(webp_bytes))


# ---------- main ----------
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()


if __name__ == "__main__":
    main()
