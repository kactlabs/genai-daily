from mcp.server.fastmcp import FastMCP
from tools import load_csv, clean_dataframe, summarize_dataframe, export_dataframe

mcp = FastMCP("data_clean_mcp")

# Store cleaned dataframe in memory (just for demo)
cleaned_dfs = {}

@mcp.tool()
def clean_data(file_path: str) -> str:
    """Loads and cleans a CSV file."""
    df = load_csv(file_path)
    cleaned = clean_dataframe(df)
    cleaned_dfs[file_path] = cleaned
    return f"Data cleaned. {len(cleaned)} rows remaining."

@mcp.tool()
def summarize_data(file_path: str) -> dict:
    """Returns summary stats and null counts of the cleaned CSV."""
    if file_path not in cleaned_dfs:
        raise ValueError("Data not cleaned yet. Run clean_data first.")
    return summarize_dataframe(cleaned_dfs[file_path])

@mcp.tool()
def export_cleaned(file_path: str, output_path: str) -> str:
    """Exports the cleaned data to a new CSV file."""
    if file_path not in cleaned_dfs:
        raise ValueError("Data not cleaned yet. Run clean_data first.")
    return export_dataframe(cleaned_dfs[file_path], output_path)

if __name__ == "__main__":
    mcp.run(transport="stdio")
