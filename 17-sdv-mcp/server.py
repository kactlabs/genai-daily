from mcp.server.fastmcp import FastMCP
from tools import generate, evaluate, visualize
import sys

# Create FastMCP instance
mcp = FastMCP("sdv_mcp")


@mcp.tool()
def sdv_generate(folder_name: str) -> str:
    try:
        return generate(folder_name)
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except RuntimeError as e:
        return f"Error: {str(e)}"


@mcp.tool()
def sdv_evaluate(folder_name: str) -> dict:
    try:
        return evaluate(folder_name)
    except FileNotFoundError as e:
        return {"error": f"File not found: {str(e)}"}
    except RuntimeError as e:
        return {"error": f"Evaluation failed: {str(e)}"}


@mcp.tool()
def sdv_visualize(folder_name: str, table_name: str, column_name: str) -> str:
    try:
        return visualize(folder_name, table_name, column_name)
    except FileNotFoundError as e:
        return f"Error: {str(e)}"
    except RuntimeError as e:
        return f"Error: {str(e)}"


#  Local test interface
def run_local():
    folder = "data"  # path to your CSVs
    print(" [LOCAL MODE] Running SDV Generate...")
    print(sdv_generate(folder))

    print("\n Running SDV Evaluate...")
    result = sdv_evaluate(folder)
    for k, v in result.items():
        print(f"{k}: {v}")

    print("\n Running SDV Visualize...")
    table_name = "guests"  # adjust if needed
    column_name = "guest_id"  # change this to a real column in your CSV
    print(sdv_visualize(folder, table_name, column_name))


if __name__ == "__main__":
    mcp.run(transport="stdio")
