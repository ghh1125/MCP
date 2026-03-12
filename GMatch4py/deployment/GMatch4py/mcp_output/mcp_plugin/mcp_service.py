import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from setup import makeExtension, scandir

mcp = FastMCP("unknown_service")


@mcp.tool(name="makeExtension", description="Auto-wrapped function makeExtension")
def makeExtension(payload: dict):
    try:
        if makeExtension is None:
            return {"success": False, "result": None, "error": "Function makeExtension is not available"}
        result = makeExtension(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="scandir", description="Auto-wrapped function scandir")
def scandir(payload: dict):
    try:
        if scandir is None:
            return {"success": False, "result": None, "error": "Function scandir is not available"}
        result = scandir(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)