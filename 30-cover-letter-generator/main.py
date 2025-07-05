from fastapi import FastAPI, Request, UploadFile, Form, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os, fitz
from io import BytesIO
from typing import Optional

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    google_api_key=os.getenv("GEMINI_API_KEY"),
)

prompt = PromptTemplate.from_template("""
You are a professional resume assistant. Based on the resume below and the job role, generate a concise and personalized cover letter.

Resume:
{resume_text}

Job Role:
{job_role}

Instructions:
- Write a professional, enthusiastic cover letter tailored for the job
- Keep it 3-4 paragraphs maximum
- Highlight achievements relevant to the job
- Keep tone formal, but friendly and confident
""")

chain = prompt | llm | StrOutputParser()

@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request, cover_letter: Optional[str] = None, filename: Optional[str] = None):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cover_letter": cover_letter,
        "filename": filename
    })

@app.post("/", response_class=RedirectResponse)
async def generate_cover_letter(
    request: Request,
    file: UploadFile = File(...),
    job_role: str = Form(...)
):
    try:
        # Read file into memory
        file_content = await file.read()
        file_stream = BytesIO(file_content)

        # Use fitz to read PDF from BytesIO directly
        with fitz.open(stream=file_stream, filetype="pdf") as doc:
            resume_text = "\n".join(page.get_text() for page in doc)

        # Generate cover letter
        cover_letter = chain.invoke({"resume_text": resume_text.strip(), "job_role": job_role})

        # Redirect with the results as query parameters
        return RedirectResponse(
            url=request.url_for("form_page").include_query_params(
                cover_letter=cover_letter,
                filename=file.filename
            ),
            status_code=303
        )

    except Exception as e:
        return RedirectResponse(
            url=request.url_for("form_page").include_query_params(
                cover_letter=f"❌ Error: {str(e)}",
                filename=None
            ),
            status_code=303
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002
    )