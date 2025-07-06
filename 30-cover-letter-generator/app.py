import os
import random
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
from serpapi import GoogleSearch
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

load_dotenv()

# Load env vars
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
RESULT_LIMIT = int(os.getenv("RESULT", 10))

# LangChain + Groq Model
model = ChatOpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
    model="llama3-70b-8192",
    temperature=0
)

# Prompt template
prompt = PromptTemplate.from_template(
    "Is the following article about GenAI, LLMs, or AI Agents? Reply YES or NO.\n\nTitle: {title}"
)
chain = prompt | model | StrOutputParser()

# FastAPI app
app = FastAPI()

class Article(BaseModel):
    title: str
    link: str

# Search and filter
def search_genai_articles():
    query = 'site:substack.com "GenAI" OR "LLM" OR "AI agent"'
    params = {
        "q": query,
        "api_key": SERPAPI_KEY,
        "engine": "google",
        "num": 30
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    organic_results = results.get("organic_results", [])

    random.shuffle(organic_results)

    filtered = []

    for result in organic_results:
        title = result.get("title", "")
        link = result.get("link", "")
        answer = chain.invoke({"title": title}).strip().lower()
        if "yes" in answer:
            filtered.append(Article(title=title, link=link))
        if len(filtered) >= RESULT_LIMIT:
            break

    return filtered

@app.get("/genai-articles", response_model=List[Article])
def get_articles():
    return search_genai_articles()
