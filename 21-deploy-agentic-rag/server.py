import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from crewai import Crew, Agent, Task, LLM
from crewai_tools import SerperDevTool

# Load .env values
load_dotenv()

# Set up LLM using Groq
llm = LLM(
    model="groq/llama3-70b-8192",  # ✅ Required format for LiteLLM to detect provider
    api_key=os.getenv("GROQ_API_KEY")  # ✅ Top-level, NOT in config
)

# Initialize FastAPI app
app = FastAPI()

# Input schema
class QueryRequest(BaseModel):
    query: str

# Global crew
crew = None

@app.on_event("startup")
async def setup_agents():
    global crew

    # Check for Serper API key (optional tool)
    tools = []
    serper_key = os.getenv("SERPER_API_KEY")
    if serper_key:
        tools.append(SerperDevTool())

    # Research agent
    researcher = Agent(
        role="Researcher",
        goal="Research the user's query and extract useful insights.",
        backstory="You're a smart assistant with excellent research skills.",
        tools=tools,
        verbose=True,
        llm=llm
    )

    # Writing agent
    writer = Agent(
        role="Writer",
        goal="Write a clear, short answer based on the research.",
        backstory="You're great at summarizing things simply.",
        verbose=True,
        llm=llm
    )

    # Define tasks
    research_task = Task(
        description="Research the user's query: {query}",
        expected_output="Bullet points or summary of findings.",
        agent=researcher
    )

    write_task = Task(
        description="Summarize the research into a clear answer: {query}",
        expected_output="A short, helpful answer.",
        agent=writer
    )

    # Crew setup
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, write_task],
        verbose=True
    )

@app.post("/query")
async def process_query(req: QueryRequest):
    try:
        result = crew.kickoff(inputs={"query": req.query})
        return {"output": result}
    except Exception as e:
        return {"error": str(e)}
