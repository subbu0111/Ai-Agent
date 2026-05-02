from duckduckgo_search import DDGS
from ai_client import ask_ai
from datetime import datetime

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return ask_ai(f"Give latest info about: {query}")

        output = ""
        for r in results:
            output += f"{r['title']}\n{r['href']}\n{r['snippet'][:200]}...\n\n"

        return output

    except Exception as e:
        return ask_ai(f"Give latest info about: {query}")


def get_news(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=3))
        output = "📰 Latest News:\n"
        for r in results:
            output += f"• {r['title']}\n  {r['url']}\n  {r['snippet'][:150]}...\n\n"
        return output
    except:
        return "❌ News unavailable"

def get_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")