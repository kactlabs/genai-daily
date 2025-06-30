from mcp.server.fastmcp import FastMCP
from tools import extract_event_info

mcp = FastMCP("event_extractor_mcp")

@mcp.tool()
def extract_events(query: str) -> str:
    """Extract event details using Serper + Gemini."""
    return extract_event_info(query)

if __name__ == "__main__":
    mcp.run(transport="stdio")
