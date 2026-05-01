from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import asyncio

# existing imports
from config import TELEGRAM_TOKEN
from tasks.reminder import set_reminder
from tasks.executor import run_command

# new imports
from tools.search import search_web
from tasks.monitor import monitor_task


# 🔐 Access control
def check_access(update):
    user_id = update.effective_user.id
    from config import ALLOWED_USER_IDS
    return user_id in ALLOWED_USER_IDS


# 🚀 START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return
    await update.message.reply_text("✅ Agent is live")


# 🧠 ASK (AI)
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /ask your question")
        return

    from ai_client import ask_ai  # lazy import

    await update.message.reply_text("🤖 Thinking...")
    reply = ask_ai(query)
    await update.message.reply_text(reply)


# ⚙️ RUN COMMAND
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    cmd = " ".join(context.args)
    if not cmd:
        await update.message.reply_text("Usage: /run command")
        return

    output = run_command(cmd)
    await update.message.reply_text(f"💻 Output:\n{output[:4000]}")


# ⏰ REMINDER
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


# 🌐 SEARCH (NEW)
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("Usage: /search query")
        return

    await update.message.reply_text("🌐 Searching...")
    result = search_web(query)

    await update.message.reply_text(result[:4000])


# 📡 MONITOR (NEW)
async def monitor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not check_access(update):
        return

    asyncio.create_task(
        monitor_task(context, update.effective_chat.id)
    )

    await update.message.reply_text("📡 Monitoring started...")


# 🚀 APP SETUP
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ask", ask))
app.add_handler(CommandHandler("run", run))
app.add_handler(CommandHandler("remind", remind))
app.add_handler(CommandHandler("search", search))
app.add_handler(CommandHandler("monitor", monitor))

print("🚀 Bot running...")
app.run_polling()