from duckduckgo_search import DDGS
from datetime import datetime

def search_web(query):
    for attempt in range(3):
        try:
            with DDGS(region='us') as ddgs:
                results = list(ddgs.text(query, max_results=30))
                answers = list(ddgs.answers(query))
            output = ''
            if answers:
                output += '💡 Answers: ' + answers[0]['answer'] + '\n\n'
            for r in results:
                output += f"{r['title']}\n{r['href']}\n{r['snippet'][:200]}...\n\n"
            return output
        except:
            if attempt < 2:
                import time
                time.sleep(2)
            continue
    return "Search unavailable"

from config import NEWSAPI_KEY

def get_news(query, timelimit=None):
    news = []
    if NEWSAPI_KEY and NEWSAPI_KEY != 'your_newsapi_key_here':
        try:
            from newsapi import NewsApiClient
            client = NewsApiClient(api_key=NEWSAPI_KEY)
            api_news = client.get_everything(q=query, language='en', sort_by='publishedAt', page_size=10)
            for article in api_news['articles'][:5]:
                news.append(f"• {article['title']} ({article['source']['name']})\n  {article['url']}\n  {article['description'][:150]}... ({article['publishedAt'][:10]})\n\n")
        except:
            pass
    for attempt in range(3):
        try:
            with DDGS(region='us') as ddgs:
                results = list(ddgs.news(query, max_results=30, timelimit=timelimit))
            if results:
                output = "📰 Latest News:\n"
                for r in results:
                    output += f"• {r['title']}\n  {r['url']}\n  {r['snippet'][:150]}... ({r['date']})\n\n"
                return output
        except:
            if attempt < 2:
                import time
                time.sleep(2)
            continue
    # Fallback to text search
    try:
        with DDGS(region='us') as ddgs:
            results = list(ddgs.text(query + ' news', max_results=10))
        output = "📰 News Fallback:\n"
        for r in results[:5]:
            output += f"• {r['title']}\n{r['href']}\n{r['snippet'][:150]}...\n\n"
        return output
    except:
        return "News unavailable"

def get_date():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")