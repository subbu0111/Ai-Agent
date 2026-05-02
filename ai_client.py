import requests
from config import OPENROUTER_API_KEY, MODEL
from tools.realtime import get_crypto_price, get_stock_price
from tools.search import get_news, get_date, search_web
from nifty500 import NIFTY500_MAP

import re

SYSTEM_PROMPT = """You are Sky, friendly elite analyst 😊. **1st RULE: NO HALLUCINATION.** STRICTLY CONTEXT + memory ONLY – never invent facts, deals, prices, news. If no data: 'No info in sources.' Casual chat OK. Helpful, concise, emojis! Deals/prices ONLY from CONTEXT. Summary first. .NS stocks. UTC given.\nEx: 'Hey! No deals in sources – monitoring! 🚀'"""

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

STOCK_NAMES = {v: k.title() for k, v in NIFTY500_MAP.items()}

def ask_ai_natural(user_input, history=None):
    context = f"CONTEXT: Date/Time: {get_date()}. "
    # Load long-term memory
    try:
        with open('/memories/repo/deals.md', 'r') as f:
            context += f"\nLong-term facts: {f.read()[:500]}"
    except:
        pass
    
    if history:
        history_str = '\n'.join([f"{msg['role']}: {msg['content']}" for msg in history[-5:]])
        context += f"\nRecent chat: {history_str}"  # Short-term memory
    
    text_lower = user_input.lower()
    words = [w.lower() for w in text_lower.split()]
    
    # ONLY fetch if stock/crypto explicit
    short_company_names = [name.split()[0].lower() for name in NIFTY500_MAP]
    stock_keywords = [s for s in short_company_names if len(s) >= 3] + ['bitcoin', 'btc', 'ethereum', 'eth', 'nifty', 'banknifty', 'nse']
    if any(kw in words for kw in stock_keywords):
        # Auto-fetch prices
        if any(s in text_lower for s in ['nifty', 'banknifty', 'nse']):
            context += get_stock_price('^NSEI') + '. BankNifty: ' + get_stock_price('^NSEBANK') + '. '
    if 'bitcoin' in text_lower or 'btc' in text_lower:
        context += get_crypto_price('bitcoin') + '. '
    if 'ethereum' in text_lower or 'eth' in text_lower:
        context += get_crypto_price('ethereum') + '. '
    
    # NSE stocks from map or uppercase tickers
    for name, ticker in NIFTY500_MAP.items():
        short_name = name.split()[0].lower()
        if short_name in words:
            price = get_stock_price(ticker)
            context += f'{ticker}: {price}. '
    
    # Generic tickers disabled - only explicit STOCK_MAP
    
    # News for stock/price queries
    if any(word in text_lower for word in ['price', 'stock', 'falling', 'rising', 'down', 'up', 'news', 'latest', 'update', 'today', 'why', 'deals', 'deal', 'contract', 'month', 'week', 'day', 'recent', 'last']) and any(kw in text_lower for kw in stock_keywords):
        query = re.sub(r'\?', '', user_input)  # Clean query
        stock_name = None
        stock_ticker = None
        for name in STOCK_MAP:
            if name in text_lower:
                stock_name = name.title()
                stock_ticker = STOCK_MAP[name]
                break
        precise_query = f"{stock_name} {query}" if stock_name else query

        if stock_ticker:
            from tools.realtime import get_stock_news
            yahoo_news = get_stock_news(stock_ticker)
            if yahoo_news:
                context += yahoo_news

        # Elite deals boost
        deal_keywords = ['deal', 'deals', 'contract', 'order', 'win']
        if any(kw in text_lower for kw in deal_keywords) and stock_name:
            sites = 'site:outlookbusiness.com OR site:economictimes.indiatimes.com OR site:moneycontrol.com OR site:business-standard.com'
            deal_query = f"{stock_name} ({sites}) (deals OR contracts OR orders OR wins OR GCC OR partnership) \"last month\" OR 2026"
            deal_news = get_news(deal_query, timelimit=None)
            if deal_news and 'unavailable' not in deal_news.lower():
                context += deal_news
            deal_web = search_web(deal_query)
            if deal_web and 'unavailable' not in deal_web.lower():
                context += deal_web

        timelimit = None  # Broad for deals
        if any(word in text_lower for word in ['day', 'today', 'hour']):
            timelimit = 'd'

        news = get_news(precise_query, timelimit)
        if news and '❌' not in news and 'unavailable' not in news.lower() and 'no' not in news.lower():
            context += news + '. '
        web = search_web(precise_query)
        if web and '❌' not in web and 'unavailable' not in web.lower() and 'no' not in web.lower():
            context += web + '. '
    
    # AI News Filter/Verify
    if 'deal_news' in context or 'Yahoo' in context:
        verify_prompt = f"Extract ONLY deals/contracts from this news: {context}. Format: ✅ [Client] $X [date]: [link/snippet]. If none: 'No verified deals.'"
        verified = ask_ai(verify_prompt)
        context += f"\n✅ Verified Deals: {verified}"

    full_prompt = f"{SYSTEM_PROMPT}\nCONTEXT: {context}\nUser: {user_input}\nSky:"
    return ask_ai(full_prompt)