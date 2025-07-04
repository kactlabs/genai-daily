from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi import FastAPI, Request, UploadFile
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_google_genai import ChatGoogleGenerativeAI
import fitz  # PyMuPDF
import os
import shutil
import re



load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY"),
    streaming=True
)

# Prompt definition
prompt = PromptTemplate.from_template("""
You are an experienced technical recruiter reviewing a candidate's resume.

Analyze the resume provided below and return a structured evaluation.

Resume:
{resume_text}

Instructions:
- Return 3 sections: **Strengths**, **Weaknesses**, and **Areas to Improve**
- Under each section, give 2–3 concise bullet points
- Use hyphens (`-`) or bullets (`•`) for each point. Do NOT use asterisks (`*`)
- Bold only section titles like **Strengths**, not the bullet points
- Avoid markdown formatting — just return clean, readable plain text

Return only the final result. No JSON, no code formatting.
""")

# Chain setup
chain: Runnable = prompt | llm | StrOutputParser()

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()

def stream_feedback(resume_text: str):
    return chain.stream({"resume_text": resume_text})

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "feedback": None})

@app.post("/", response_class=StreamingResponse)
async def upload_resume(request: Request, file: UploadFile):
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = extract_text_from_pdf(file_path)
        resume_text = re.sub(r"[＊∗✱*]", "", result)
        os.remove(file_path)

        return StreamingResponse(stream_feedback(resume_text), media_type="text/plain")

    except Exception as e:
        return StreamingResponse(iter([f"❌ Error: {str(e)}"]), media_type="text/plain")
