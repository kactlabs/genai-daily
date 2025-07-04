import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

def ask_gemini(question: str) -> str:
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        return "GEMINI_API_KEY not found in .env"

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

        prompt = PromptTemplate(
            input_variables=["question"],
            template="You are an expert AI. Answer this question:\n\n{question}"
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(question)
        return response
    except Exception as e:
        return f"Error: {e}"
