import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

llm = ChatGroq(
    model="LLaMA3-70b-8192",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

mongo_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template="""
You are a Python developer writing PyMongo queries.

Given the MongoDB schema:
{schema}

Write only the executable PyMongo code in Python (no explanation). Use `pymongo`, `datetime`, and `aggregate` if needed.

Question:
{question}

Return only valid code in a single Python block.
"""
)

code_extractor_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
You are a code extractor bot.

Extract only the valid Python code from the following text.
Do not include any explanations or markdown formatting like ```python or ```.
Return only raw Python code.

Text:
{text}
"""
)

@app.get("/", response_class=HTMLResponse)
async def form_ui(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def generate_query(request: Request, schema: str = Form(...), question: str = Form(...)):
    # First prompt: generate raw output (includes explanation + code)
    prompt = mongo_prompt.format(schema=schema, question=question)
    full_output = llm.invoke(prompt).content  # or just .invoke(prompt) based on LLM return type

    # Second prompt: extract only the Python code
    code_only_prompt = code_extractor_prompt.format(text=full_output)
    clean_code = llm.invoke(code_only_prompt).content

    # Render only the clean code
    return templates.TemplateResponse("index.html", {
        "request": request,
        "schema": schema,
        "question": question,
        "response": clean_code
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
