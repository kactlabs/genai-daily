import os
import pandas as pd
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

llm = ChatGroq(
    model="LLaMA3-70b-8192",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Store session state in memory (note: for production use Redis or DB)
session_state = {
    "filename": None,
    "df": None,
    "chat_history": []
}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "filename": session_state["filename"],
        "chat_history": session_state["chat_history"]
    })


@app.post("/upload", response_class=HTMLResponse)
async def upload_csv(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    df = pd.read_csv(file_path)
    session_state["filename"] = file.filename
    session_state["df"] = df
    session_state["chat_history"] = []

    return RedirectResponse("/", status_code=302)


@app.post("/ask", response_class=HTMLResponse)
async def ask_question(request: Request, question: str = Form(...)):
    df = session_state["df"]

    if df is None:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "filename": None,
            "chat_history": [],
            "error": "Please upload a CSV file first."
        })

    csv_preview = df.to_csv(index=False)

    prompt = PromptTemplate(
        input_variables=["question", "csv_data"],
        template="""
You are a data analyst.

Here is a CSV dataset:
{csv_data}

Now, answer the following question:
{question}

Only return the answer. Do not explain or include Python code.
"""
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run({"question": question, "csv_data": csv_preview}).strip()

    session_state["chat_history"].append({"user": question, "bot": response})

    return RedirectResponse("/", status_code=302)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8002)