import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from docs.source.conf import get_type_hints

mcp = FastMCP("unknown_service")


@mcp.tool(name="get_type_hints", description="Auto-wrapped function get_type_hints")
def get_type_hints(payload: dict):
    try:
        if get_type_hints is None:
            return {"success": False, "result": None, "error": "Function get_type_hints is not available"}
        result = get_type_hints(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)