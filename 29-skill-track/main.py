from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi import FastAPI, Request, UploadFile, Form
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import fitz
import os
import shutil

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Store result temporarily (in memory)
temp_feedback = ""

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text.strip()

def get_feedback(resume_text: str) -> str:
    prompt = PromptTemplate.from_template("""
    You are an expert resume reviewer. Review the resume text below and return a **brief** evaluation.

    Resume:
    {resume_text}

    Instructions:
    - Provide feedback in **3 sections**: **Strengths** and **Weaknesses** and **Areas to Improve**.
    - Use **clear, concise language** and avoid jargon.
    - Each section should have **no more than 3 concise points**
    - Use clear sentences, no asterisk (*) or markdown bullets
    - Bold the section titles (e.g., **Strengths**, **Areas to Improve**)
    - Keep the feedback short and easy to scan

    Return the result as plain readable text.
    """)
    chain = prompt | llm
    return chain.invoke({"resume_text": resume_text}).content

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    global temp_feedback
    feedback = temp_feedback
    temp_feedback = ""  # Clear feedback after rendering
    return templates.TemplateResponse("index.html", {"request": request, "feedback": feedback})

@app.post("/", response_class=HTMLResponse)
async def upload_resume(request: Request, file: UploadFile):
    global temp_feedback
    try:
        file_path = f"temp_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        resume_text = extract_text_from_pdf(file_path)
        feedback_raw = get_feedback(resume_text)
        temp_feedback = feedback_raw.replace("*", "")
        os.remove(file_path)

        # Redirect to home to show and then clear feedback
        return RedirectResponse(url="/", status_code=302)

    except Exception as e:
        temp_feedback = f"❌ Error: {str(e)}"
        return RedirectResponse(url="/", status_code=302)
