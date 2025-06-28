from mcp.server.fastmcp import FastMCP
from tools import get_weather_for_city

mcp = FastMCP("weather_mcp")

@mcp.tool()
def get_weather(city: str) -> str:
    """Returns current weather for a given city using OpenWeather API."""
    return get_weather_for_city(city)

if __name__ == "__main__":
    mcp.run(transport="stdio")
