import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ✅ Correct API key usage and model name
api_key = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model="LLaMA3-70b-8192", groq_api_key=api_key)

# Prompt Template
prompt = PromptTemplate(
    input_variables=["message"],
    template="""
You are a customer support assistant. Reply to the following customer message in a good manner tone.

Customer message:
"{message}"

Support reply:
"""
)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "", "response": ""})

@app.post("/", response_class=HTMLResponse)
async def generate_reply(request: Request, message: str = Form(...)):
    formatted_prompt = prompt.format(message=message)
    response = llm.invoke(formatted_prompt).content
    return templates.TemplateResponse("index.html", {
        "request": request,
        "message": message,
        "response": response
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
