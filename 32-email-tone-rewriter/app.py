import os 
from fastapi import FastAPI,Request,Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableMap

load_dotenv()

app= FastAPI()

templates = Jinja2Templates(directory="templates")

api_key = os.getenv("GROQ_API_KEY")
print(api_key)
llm = ChatGroq(model="llama3-70b-8192",api_key=api_key,temperature=0.1)

prompt = PromptTemplate.from_template("""
You are an expert email tone editor.

Rewrite the email below into 3 tones:
1. Formal
2. Friendly
3. Assertive

Original Email:
{email}

Return in this format:

**Formal Version:**
<formal_email>

**Friendly Version:**
<friendly_email>

**Assertive Version:**
<assertive_email>
""")


chain = RunnableMap({"email": lambda x: x}) | prompt | llm | StrOutputParser()


@app.get("/",response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,"result":None})

@app.post("/",response_class=HTMLResponse)
async def generate_email(request: Request, email: str = Form(...)):
    result = chain.invoke({"email":email})
    return templates.TemplateResponse("index.html", {"request": request, "result":result})
