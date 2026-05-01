from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from config import TELEGRAM_TOKEN
from ai_client import ask_ai
from security import is_allowed
from tasks.executor import run_command
from tasks.reminder import set_reminder
import asyncio

def check_access(update):
    user_id = update.effective_user.id
    return is_allowed(user_id)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return
    await update.message.reply_text("✅ Agent is live")

async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /ask your question")
        return

    await update.message.reply_text("🤖 Thinking...")
    reply = ask_ai(query)
    await update.message.reply_text(reply)

async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    cmd = " ".join(context.args)
    if not cmd:
        await update.message.reply_text("Usage: /run command")
        return

    output = run_command(cmd)
    await update.message.reply_text(f"💻 Output:\n{output[:4000]}")

async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /remind seconds message")
        return

    seconds = int(context.args[0])
    msg = " ".join(context.args[1:])

    asyncio.create_task(
        set_reminder(seconds, msg, context, update.effective_chat.id)
    )

    await update.message.reply_text("⏰ Reminder set")

app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("run", run))
app.add_handler(CommandHandler("remind", remind))

print("🚀 Bot running...")
app.run_polling()