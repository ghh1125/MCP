import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from scripts.SequencePatternMatching import loadUniprotDB, volumeScoring, peptideSearching

mcp = FastMCP("unknown_service")


@mcp.tool(name="loadUniprotDB", description="Auto-wrapped function loadUniprotDB")
def loadUniprotDB(payload: dict):
    try:
        if loadUniprotDB is None:
            return {"success": False, "result": None, "error": "Function loadUniprotDB is not available"}
        result = loadUniprotDB(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="peptideSearching", description="Auto-wrapped function peptideSearching")
def peptideSearching(payload: dict):
    try:
        if peptideSearching is None:
            return {"success": False, "result": None, "error": "Function peptideSearching is not available"}
        result = peptideSearching(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="volumeScoring", description="Auto-wrapped function volumeScoring")
def volumeScoring(payload: dict):
    try:
        if volumeScoring is None:
            return {"success": False, "result": None, "error": "Function volumeScoring is not available"}
        result = volumeScoring(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)