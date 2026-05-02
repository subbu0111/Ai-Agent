from duckduckgo_search import DDGS
from ai_client import ask_ai

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))

        if not results:
            # fallback to AI
            return ask_ai(f"Give latest info about: {query}")

        output = ""
        for r in results:
            output += f"{r['title']}\n{r['href']}\n\n"

        return output

    except Exception as e:
        # fallback to AI
        return ask_ai(f"Give latest info about: {query}")