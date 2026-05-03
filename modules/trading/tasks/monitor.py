import asyncio
from tools.search import search_web

async def monitor_task(context, chat_id):
    while True:
        try:
            data = search_web("NIFTY market news today")

            await context.bot.send_message(
                chat_id=chat_id,
                text=f"📊 Update:\n{data[:1000]}"
            )

        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=str(e))

        await asyncio.sleep(300)  # every 5 mins