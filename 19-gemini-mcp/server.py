from mcp.server.fastmcp import FastMCP
from tools import ask_gemini
from langchain_google_genai import ChatGoogleGenerativeAI

mcp = FastMCP("langchain_gemini_mcp")

@mcp.tool()
def gemini_chat(question: str) -> str:
    """Ask a question to Gemini using LangChain and return the answer."""
    return ask_gemini(question)

if __name__ == "__main__":
    mcp.run(transport="stdio")
