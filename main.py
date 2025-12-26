from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, ContextTypes, filters
import requests
import os
from datetime import datetime
from config import GROUP_ID, CONFIDENCE_THRESHOLD, TIMEZONE
from vision import similarity_score
from attendance import get_current_slot, already_checked, save_attendance
from report import report_today, report_week

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return

    slot = get_current_slot()
    if not slot:
        await update.message.reply_text(
            "❌ Ngoài khung giờ điểm danh.\n❌ Outside attendance time."
        )
        return

    user = update.effective_user
    date = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    if already_checked(user.id, date, slot):
        await update.message.reply_text(
            "⚠️ Bạn đã điểm danh ca này.\n⚠️ You already checked in."
        )
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_bytes = requests.get(file.file_path).content

    score = similarity_score(img_bytes)

    if score < CONFIDENCE_THRESHOLD:
        await context.bot.send_message(
            user.id,
            "❌ Chưa nhận diện rõ vật yêu cầu. Vui lòng chụp lại.\n"
            "❌ Required object not detected clearly. Please retake."
        )
        return

    save_attendance({
        "user_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "date": date,
        "slot": slot,
        "confidence": score,
        "photo_file_id": photo.file_id,
        "created_at": datetime.now(TIMEZONE).isoformat()
    })

    await update.message.reply_text(
        "✅ Điểm danh thành công.\n✅ Attendance recorded successfully."
    )

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = report_today()
    msg = "📅 Hôm nay / Today\n"
    for k, v in data.items():
        msg += f"\n{k}: {len(v)}"
    await update.message.reply_text(msg)

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = report_week()
    msg = "📊 7 ngày / Last 7 days\n"
    for name, count in data.items():
        msg += f"\n{name}: {count}"
    await update.message.reply_text(msg)

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(CommandHandler("today", today))
app.add_handler(CommandHandler("week", week))

app.run_webhook(
    listen="0.0.0.0",
    port=int(os.getenv("PORT", 10000)),
    webhook_url=os.getenv("WEBHOOK_URL")
)

