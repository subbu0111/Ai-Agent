import requests
from config import OPENROUTER_API_KEY, MODEL
from tools.realtime import get_crypto_price, get_stock_price
from tools.search import get_news, get_date, search_web

SYSTEM_PROMPT = """You are a helpful, conversational assistant for stock/crypto/news queries. Use provided CONTEXT for real-time facts (prices, news, date). Respond naturally, concisely. If asking about stocks like TCS/NIFTY add .NS or ^NSEI. Format prices/news clearly. Current date/time included."""

def ask_ai(prompt):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI Error: {str(e)}"

def ask_ai_natural(user_input):
    context = f"CONTEXT: Date/Time: {get_date()}. "
    
    text_lower = user_input.lower()
    
    # Auto-fetch prices
    if any(s in text_lower for s in ['nifty', 'banknifty', 'nse']):
        context += get_stock_price('^NSEI') + '. BankNifty: ' + get_stock_price('^NSEBANK') + '. '
    if 'bitcoin' in text_lower or 'btc' in text_lower:
        context += get_crypto_price('bitcoin') + '. '
    if 'ethereum' in text_lower or 'eth' in text_lower:
        context += get_crypto_price('ethereum') + '. '
    
    # NSE stocks (e.g. TCS)
    import re
    tickers = re.findall(r'\b[A-Z]{2,5}\b', user_input)
    for ticker in tickers[:2]:  # Top 2
        try:
            price = get_stock_price(f'{ticker}.NS')
            if 'failed' not in price.lower():
                context += f'{ticker}.NS: {price}. '
        except:
            pass
    
    # News/latest
    if any(word in text_lower for word in ['news', 'latest', 'update', 'today']):
        context += get_news(user_input) + '. '
    
    # General search
    if any(word in text_lower for word in ['search', 'info', 'what is']):
        context += search_web(user_input) + '. '
    
    full_prompt = f"{SYSTEM_PROMPT}\n{context}\nUser: {user_input}\nAssistant:"
    return ask_ai(full_prompt)