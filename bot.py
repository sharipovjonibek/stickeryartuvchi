import io, os, time
from PIL import Image
from telegram import Update, InputSticker, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TOKEN")  # set this in Railway Variables

def to_webp_512(image_bytes: bytes) -> bytes:
    im = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    im.thumbnail((512, 512))
    out = io.BytesIO()
    im.save(out, format="WEBP")
    out.seek(0)
    return out.read()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Rasm yuboring — men uni yangi stiker to‘plamiga qo‘shaman. 📷➡️🎟️")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    me = await context.bot.get_me()

    set_name = f"uz_user_{user.id}_{int(time.time())}_by_{me.username}".lower()
    set_title = f"{(user.first_name or 'Foydalanuvchi')} stiker to‘plami"

    tfile = await update.message.photo[-1].get_file()
    original = await tfile.download_as_bytearray()
    webp_bytes = to_webp_512(original)

    # v21: include format="static" here
    input_sticker = InputSticker(
        sticker=io.BytesIO(webp_bytes),
        emoji_list=["🙂"],
        format="static",
    )

    try:
        # v21: DO NOT pass sticker_format= here
        await context.bot.create_new_sticker_set(
            user_id=user.id,
            name=set_name,
            title=set_title,
            stickers=[input_sticker],
        )
    except Exception as e:
        print("Create sticker set error:", e)
        await update.message.reply_text("Kechirasiz, yangi to‘plam yaratishda xatolik yuz berdi.")
        return

    pack_url = f"https://t.me/addstickers/{set_name}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("➕ To‘plamni qo‘shish", url=pack_url)]])
    await update.message.reply_text(f"✅ Yangi to‘plam yaratildi: «{set_title}»", reply_markup=kb)
    await update.message.reply_sticker(sticker=io.BytesIO(webp_bytes))

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("TOKEN is missing")
    main()
