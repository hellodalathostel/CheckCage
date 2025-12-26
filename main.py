import os
import requests
from datetime import datetime

from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    CommandHandler,
    ContextTypes,
    filters,
)

from config import GROUP_ID, CONFIDENCE_THRESHOLD, TIMEZONE
from vision import similarity_score
from attendance import get_current_slot, already_checked, save_attendance
from report import report_today, report_week

BOT_TOKEN = os.getenv("BOT_TOKEN")


# =========================
# HANDLE PHOTO (ATTENDANCE)
# =========================
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_ID:
        return

    slot = get_current_slot()
    if not slot:
        await update.message.reply_text(
            "❌ Ngoài khung giờ điểm danh.\n"
            "❌ Outside attendance time."
        )
        return

    user = update.effective_user
    today = datetime.now(TIMEZONE).strftime("%Y-%m-%d")

    if already_checked(user.id, today, slot):
        await update.message.reply_text(
            "⚠️ Bạn đã điểm danh ca này.\n"
            "⚠️ You already checked in for this slot."
        )
        return

    photo = update.message.photo[-1]
    file = await photo.get_file()
    img_bytes = requests.get(file.file_path).content

    score = similarity_score(img_bytes)

    if score < CONFIDENCE_THRESHOLD:
        await context.bot.send_message(
            chat_id=user.id,
            text=(
                "❌ Không nhận diện rõ vật yêu cầu. Vui lòng chụp lại.\n"
                "❌ Required object not detected clearly. Please retake the photo."
            ),
        )
        return

    save_attendance({
        "user_id": user.id,
        "full_name": user.full_name,
        "username": user.username,
        "date": today,
        "slot": slot,
        "confidence": score,
        "photo_file_id": photo.file_id,
        "created_at": datetime.now(TIMEZONE).isoformat(),
    })

    await update.message.reply_text(
        "✅ Điểm danh thành công.\n"
        "✅ Attendance recorded successfully."
    )


# =========================
# REPORT: TODAY
# =========================
async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = report_today()

    msg = (
        f"📅 Điểm danh hôm nay\n"
        f"📅 Attendance today\n"
    )

    for slot, users in data.items():
        msg += f"\n• {slot}: {len(users)}"

    await update.message.reply_text(msg)


# =========================
# REPORT: WEEK
# =========================
async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = report_week()

    msg = (
        "📊 Thống kê 7 ngày gần nhất\n"
        "📊 Attendance last 7 days\n\n"
    )

    for name, count in data.items():
        msg += f"- {name}: {count}\n"

    await update.message.reply_text(msg)


# =========================
# MAIN ENTRY
# =========================
def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("week", week))

    application.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
        webhook_url=os.environ.get("WEBHOOK_URL"),
    )


if __name__ == "__main__":
    main()
