from duckduckgo_search import DDGS

def search_web(query):
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=3)

        output = ""
        for r in results:
            output += f"{r['title']}\n{r['href']}\n\n"

        return output if output else "No results found"

    except Exception as e:
        return str(e)