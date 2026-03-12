import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

# No imports available

mcp = FastMCP("unknown_service")


    @mcp.tool(name="core", description="Default core function")
    def core(*args, **kwargs):
        return {"success": False, "result": None, "error": "no_import_available"}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)