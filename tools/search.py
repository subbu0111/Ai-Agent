from duckduckgo_search import DDGS
from datetime import datetime

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            return "No web results found."

        output = ""
        for r in results:
            output += f"{r['title']}\n{r['href']}\n{r['snippet'][:200]}...\n\n"

        return output

    except Exception as e:
        return "❌ Search unavailable"


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