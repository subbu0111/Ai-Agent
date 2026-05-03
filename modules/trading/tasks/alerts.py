import asyncio
from modules.trading.tools.realtime import get_stock_price

async def monitor_price(asset, threshold, context, chat_id):
    while True:
        price_str = get_stock_price(asset)
        try:
            price = float(price_str.split('₹')[1].split()[0])
            if price <= threshold:
                await context.bot.send_message(chat_id, f"🚨 ALERT: {asset} hit ₹{price} (threshold {threshold})")
                break
        except:
            pass
        await asyncio.sleep(60)  # Check minutely