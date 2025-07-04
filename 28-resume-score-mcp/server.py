from mcp.server.fastmcp import FastMCP
from tools import index_resume, search_resumes

mcp = FastMCP("resume_semantic_mcp")

@mcp.tool()
def add_resume(pdf_path: str) -> str:
    """Extracts and indexes resume from PDF file into Qdrant."""
    return index_resume(pdf_path)

@mcp.tool()
def find_resumes(job_description: str) -> list:
    """Find resumes that semantically match a given job description."""
    return search_resumes(job_description)

if __name__ == "__main__":
    mcp.run(transport="stdio")
