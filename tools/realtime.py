import requests
import yfinance as yf

def safe_return(text):
    if not text:
        return "❌ No data available"
    return text


def get_crypto_price(symbol):
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {"ids": symbol, "vs_currencies": "usd"}

        res = requests.get(url, params=params, timeout=5).json()

        if symbol not in res:
            return "❌ Crypto not found"

        price = res[symbol].get("usd")
        if price is None:
            return "❌ Crypto price unavailable"

        return f"{symbol.upper()} Price: ${price}"

    except Exception:
        return "❌ Failed to fetch crypto price"


def get_stock_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice') or info.get('currentPrice')
        if price is None:
            return "❌ Market closed or data unavailable"
        return f"{symbol} Price: {price}"
    except Exception:
        return "❌ Failed to fetch stock price"