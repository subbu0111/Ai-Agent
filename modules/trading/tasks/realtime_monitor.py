import asyncio
from modules.trading.tools.realtime import get_crypto_price, get_stock_price

async def track_asset(context, chat_id, asset):
    last = None

    while True:
        if asset == "bitcoin":
            data = get_crypto_price("bitcoin")
        else:
            data = get_stock_price(asset)

        if data and data != last:
            await context.bot.send_message(chat_id=chat_id, text=data)
            last = data

        await asyncio.sleep(10)