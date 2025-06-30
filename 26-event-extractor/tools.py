import os
import requests
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load keys from .env file
load_dotenv()

def search_events(query: str, max_results=5) -> str:
    """Use Serper.dev API to get real-time search results for the query."""
    api_key = os.getenv("SERPER_API_KEY")
    if not api_key:
        return "❌ SERPER_API_KEY not found in .env"

    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "q": query
    }

    try:
        res = requests.post(url, json=data, headers=headers)
        res.raise_for_status()
        items = res.json().get("organic", [])[:max_results]
        if not items:
            return "❌ No search results found"

        results = []
        for item in items:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")
            results.append(f"{title}\n{snippet}\n{link}\n")

        return "\n".join(results)
    except Exception as e:
        return f"❌ Serper API search failed: {e}"

def summarize_events(raw_text: str) -> str:
    """Summarize raw search text into structured event info using Gemini."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        return "❌ GEMINI_API_KEY not found in .env"

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

    prompt = PromptTemplate(
        input_variables=["content"],
        template="""
You are an AI assistant. Extract and list any upcoming tech events or conferences from the following content.

Each event should include:
- Event name
- Date (if available)
- Location (if available)
- Website or link (if available)

Here is the content:
{content}

Return a clean list like:
1. Event Name
   Date: ...
   Location: ...
   Link: ...
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({"content": raw_text[:8000]})

def extract_event_info(query: str) -> str:
    """Main function to search and summarize event information."""
    raw = search_events(query)
    if raw.startswith("❌"):
        return raw
    return summarize_events(raw)

if __name__ == "__main__":
    query = "Tech conferences in India 2025"
    print(extract_event_info(query))
