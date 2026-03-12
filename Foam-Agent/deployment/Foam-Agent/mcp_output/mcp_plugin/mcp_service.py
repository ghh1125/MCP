import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from init_database import parse_args, run_command, main
from foambench_main import parse_args, run_command, main
from database.script.faiss_tutorials_structure import extract_field, tokenize, main
from database.script.faiss_tutorials_details import extract_field, tokenize, main

mcp = FastMCP("unknown_service")


@mcp.tool(name="main", description="Auto-wrapped function main")
def main(payload: dict):
    try:
        if main is None:
            return {"success": False, "result": None, "error": "Function main is not available"}
        result = main(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_args", description="Auto-wrapped function parse_args")
def parse_args(payload: dict):
    try:
        if parse_args is None:
            return {"success": False, "result": None, "error": "Function parse_args is not available"}
        result = parse_args(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="run_command", description="Auto-wrapped function run_command")
def run_command(payload: dict):
    try:
        if run_command is None:
            return {"success": False, "result": None, "error": "Function run_command is not available"}
        result = run_command(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="main", description="Auto-wrapped function main")
def main(payload: dict):
    try:
        if main is None:
            return {"success": False, "result": None, "error": "Function main is not available"}
        result = main(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_args", description="Auto-wrapped function parse_args")
def parse_args(payload: dict):
    try:
        if parse_args is None:
            return {"success": False, "result": None, "error": "Function parse_args is not available"}
        result = parse_args(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="run_command", description="Auto-wrapped function run_command")
def run_command(payload: dict):
    try:
        if run_command is None:
            return {"success": False, "result": None, "error": "Function run_command is not available"}
        result = run_command(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="extract_field", description="Auto-wrapped function extract_field")
def extract_field(payload: dict):
    try:
        if extract_field is None:
            return {"success": False, "result": None, "error": "Function extract_field is not available"}
        result = extract_field(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="main", description="Auto-wrapped function main")
def main(payload: dict):
    try:
        if main is None:
            return {"success": False, "result": None, "error": "Function main is not available"}
        result = main(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="tokenize", description="Auto-wrapped function tokenize")
def tokenize(payload: dict):
    try:
        if tokenize is None:
            return {"success": False, "result": None, "error": "Function tokenize is not available"}
        result = tokenize(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="extract_field", description="Auto-wrapped function extract_field")
def extract_field(payload: dict):
    try:
        if extract_field is None:
            return {"success": False, "result": None, "error": "Function extract_field is not available"}
        result = extract_field(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="main", description="Auto-wrapped function main")
def main(payload: dict):
    try:
        if main is None:
            return {"success": False, "result": None, "error": "Function main is not available"}
        result = main(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="tokenize", description="Auto-wrapped function tokenize")
def tokenize(payload: dict):
    try:
        if tokenize is None:
            return {"success": False, "result": None, "error": "Function tokenize is not available"}
        result = tokenize(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)