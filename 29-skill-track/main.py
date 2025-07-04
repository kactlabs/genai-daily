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
You are an expert resume reviewer. Review the resume text below and return a **brief** evaluation.

Resume:
{resume_text}

Instructions:
- Provide feedback in **3 sections**: **Strengths**, **Weaknesses**, and **Areas to Improve**
- Use **clear, concise language** and avoid jargon
- Each section should have **no more than 3 concise points**
- No asterisks (*), no markdown bullets
- Bold the section titles (e.g., Strengths, Weaknesses)

Return only readable plain text, well formatted.
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
        resume_text = result.replace("*","")
        os.remove(file_path)

        return StreamingResponse(stream_feedback(resume_text), media_type="text/plain")

    except Exception as e:
        return StreamingResponse(iter([f"❌ Error: {str(e)}"]), media_type="text/plain")
