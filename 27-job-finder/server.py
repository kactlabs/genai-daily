from mcp.server.fastmcp import FastMCP
from tools import search_jobs, filter_jobs_by_skills, summarize_top_jobs

mcp = FastMCP("job_finder_mcp")

@mcp.tool()
def find_jobs(title: str, location: str) -> list:
    return search_jobs(title, location)

@mcp.tool()
def filter_jobs(jobs: list, skills: list) -> list:
    return filter_jobs_by_skills(jobs, skills)

@mcp.tool()
def summarize_jobs(jobs: list) -> str:
    return summarize_top_jobs(jobs)

if __name__ == "__main__":
    mcp.run(transport="stdio")
