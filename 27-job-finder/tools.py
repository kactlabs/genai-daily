import os
import requests
from dotenv import load_dotenv
from typing import List
from langchain.llms import GooglePalm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")

def search_jobs(title: str, location: str, max_results: int = 10) -> List[dict]:
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    query = f"{title} jobs in {location}"

    res = requests.post(url, headers=headers, json={"q": query})
    results = res.json()
    
    jobs = []
    for item in results.get("organic", [])[:max_results]:
        jobs.append({
            "title": item.get("title"),
            "link": item.get("link"),
            "snippet": item.get("snippet")
        })
    return jobs

def filter_jobs_by_skills(jobs: List[dict], skills: List[str]) -> List[dict]:
    filtered = []
    for job in jobs:
        text = f"{job['title']} {job['snippet']}".lower()
        if any(skill.lower() in text for skill in skills):
            filtered.append(job)
    return filtered

def summarize_top_jobs(jobs: List[dict]) -> str:
    if not jobs:
        return "No jobs to summarize."

    text_blob = "\n".join([f"{j['title']}: {j['snippet']}" for j in jobs[:5]])

    llm = GooglePalm(google_api_key=os.getenv("GEMINI_API_KEY"), temperature=0.7)
    prompt = PromptTemplate.from_template("Summarize these jobs:\n{text}")
    chain = LLMChain(llm=llm, prompt=prompt)

    return chain.run(text=text_blob)
