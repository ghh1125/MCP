import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from setup import read
from additional_resources.build_emoji_lexicon import get_list_from_file, append_to_file, pad_ref

mcp = FastMCP("unknown_service")


@mcp.tool(name="read", description="Auto-wrapped function read")
def read(payload: dict):
    try:
        if read is None:
            return {"success": False, "result": None, "error": "Function read is not available"}
        result = read(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="append_to_file", description="Auto-wrapped function append_to_file")
def append_to_file(payload: dict):
    try:
        if append_to_file is None:
            return {"success": False, "result": None, "error": "Function append_to_file is not available"}
        result = append_to_file(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_list_from_file", description="Auto-wrapped function get_list_from_file")
def get_list_from_file(payload: dict):
    try:
        if get_list_from_file is None:
            return {"success": False, "result": None, "error": "Function get_list_from_file is not available"}
        result = get_list_from_file(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="pad_ref", description="Auto-wrapped function pad_ref")
def pad_ref(payload: dict):
    try:
        if pad_ref is None:
            return {"success": False, "result": None, "error": "Function pad_ref is not available"}
        result = pad_ref(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)