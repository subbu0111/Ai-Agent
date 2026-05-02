from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
import asyncio

from config import TELEGRAM_TOKEN, ALLOWED_USER_IDS
from ai_client import ask_ai_natural
from tasks.reminder import set_reminder
from tasks.executor import run_command
from tasks.realtime_monitor import track_asset


def check_access(update):
    return update.effective_user.id in ALLOWED_USER_IDS


def safe_reply(text):
    if not text or text.strip() == "":
        return "❌ No response generated"
    return text


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    text = update.message.text.lower()
    print("Incoming:", text)

    # ⚙️ RUN COMMAND
    if text.startswith("run "):
        cmd = text.replace("run ", "")
        output = run_command(cmd)
        await update.message.reply_text(safe_reply(output))
        return

    # ⏰ REMINDER
    if "remind me" in text:
        try:
            parts = text.split()
            sec = int([x for x in parts if x.isdigit()][0])
            msg = text.split(str(sec))[-1]

            asyncio.create_task(
                set_reminder(sec, msg, context, update.effective_chat.id)
            )

            await update.message.reply_text("⏰ Reminder set")
        except:
            await update.message.reply_text("❌ Failed to set reminder")
        return

    # � TRACKING (keep special)
    if "track" in text:
        if "bitcoin" in text:
            asset = "bitcoin"
        elif "bank" in text and "nifty" in text:
            asset = "^NSEBANK"
        elif "nifty" in text:
            asset = "^NSEI"
        else:
            await update.message.reply_text("❌ Unknown asset")
            return

        asyncio.create_task(
            track_asset(context, update.effective_chat.id, asset)
        )

        await update.message.reply_text(f"📡 Tracking {asset}")
        return

    # 🧠 Natural AI (handles prices/news/date/stocks naturally)
    await update.message.reply_text("🤖 Thinking...")
    reply = ask_ai_natural(update.message.text)  # Use original text (not lower)
    await update.message.reply_text(safe_reply(reply))


app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("🚀 STABLE REAL-TIME BOT RUNNING...")
app.run_polling()