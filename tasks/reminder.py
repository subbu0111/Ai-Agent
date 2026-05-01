import asyncio

async def set_reminder(seconds, message, context, chat_id):
    await asyncio.sleep(seconds)
    await context.bot.send_message(chat_id=chat_id, text=f"⏰ Reminder: {message}")