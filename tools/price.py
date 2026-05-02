import requests

def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "bitcoin",
            "vs_currencies": "usd"
        }

        res = requests.get(url, params=params).json()
        price = res["bitcoin"]["usd"]

        return f"BTC Price: ${price}"

    except Exception as e:
        return f"Error: {str(e)}"