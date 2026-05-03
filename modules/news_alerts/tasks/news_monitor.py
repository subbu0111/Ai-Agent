import asyncio
import json
from datetime import datetime
from modules.trading.tools.search import get_news
from telegram.ext import ContextTypes

async def proactive_news(chat_id, context: ContextTypes.DEFAULT_TYPE, interests=None):
    if interests is None:
        interests = ['deals', 'news']
    while True:
        try:
            now = datetime.now().hour
            if now % 2 == 0:  # Every 2h
                for interest in interests:
                    news = get_news(f"{interest} latest india", timelimit='h')
                    if news and any(kw in news.lower() for kw in ['deal', 'breaking', 'alert']):
                        msg = f"🚨 {interest.upper()} Alert: {news[:400]}"
                        await context.bot.send_message(chat_id=chat_id, text=msg)
        except Exception as e:
            print(f"News monitor error: {e}")
        await asyncio.sleep(7200)  # 2h

async def start_proactive(chat_id, context, interests):
    task = asyncio.create_task(proactive_news(chat_id, context, interests))
    # Store task ref if needed
    return task
