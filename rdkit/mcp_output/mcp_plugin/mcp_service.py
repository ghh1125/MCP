import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from Regress.Scripts.new_timings import data
from Web.RDExtras.MolImage import svg, gif
from Web.RDExtras.MolDepict import page
from Projects.DbCLI.CreateDb import initParser, CreateDb
from Projects.DbCLI.SearchDb import GetMolsFromSDFile, GetNeighborLists, GetMolsFromSmilesFile
from Code.DataManip.MetricMatrixCalc.Wrap.testMatricCalc import feq
from Code.DataStructs.Wrap.testBV import feq
from Code.DataStructs.Wrap.testSparseIntVect import feq

mcp = FastMCP("unknown_service")


@mcp.tool(name="data", description="Auto-wrapped function data")
def data(payload: dict):
    try:
        if data is None:
            return {"success": False, "result": None, "error": "Function data is not available"}
        result = data(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="gif", description="Auto-wrapped function gif")
def gif(payload: dict):
    try:
        if gif is None:
            return {"success": False, "result": None, "error": "Function gif is not available"}
        result = gif(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="svg", description="Auto-wrapped function svg")
def svg(payload: dict):
    try:
        if svg is None:
            return {"success": False, "result": None, "error": "Function svg is not available"}
        result = svg(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="page", description="Auto-wrapped function page")
def page(payload: dict):
    try:
        if page is None:
            return {"success": False, "result": None, "error": "Function page is not available"}
        result = page(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="CreateDb", description="Auto-wrapped function CreateDb")
def CreateDb(payload: dict):
    try:
        if CreateDb is None:
            return {"success": False, "result": None, "error": "Function CreateDb is not available"}
        result = CreateDb(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="initParser", description="Auto-wrapped function initParser")
def initParser(payload: dict):
    try:
        if initParser is None:
            return {"success": False, "result": None, "error": "Function initParser is not available"}
        result = initParser(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="GetMolsFromSDFile", description="Auto-wrapped function GetMolsFromSDFile")
def GetMolsFromSDFile(payload: dict):
    try:
        if GetMolsFromSDFile is None:
            return {"success": False, "result": None, "error": "Function GetMolsFromSDFile is not available"}
        result = GetMolsFromSDFile(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="GetMolsFromSmilesFile", description="Auto-wrapped function GetMolsFromSmilesFile")
def GetMolsFromSmilesFile(payload: dict):
    try:
        if GetMolsFromSmilesFile is None:
            return {"success": False, "result": None, "error": "Function GetMolsFromSmilesFile is not available"}
        result = GetMolsFromSmilesFile(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="GetNeighborLists", description="Auto-wrapped function GetNeighborLists")
def GetNeighborLists(payload: dict):
    try:
        if GetNeighborLists is None:
            return {"success": False, "result": None, "error": "Function GetNeighborLists is not available"}
        result = GetNeighborLists(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="feq", description="Auto-wrapped function feq")
def feq(payload: dict):
    try:
        if feq is None:
            return {"success": False, "result": None, "error": "Function feq is not available"}
        result = feq(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="feq", description="Auto-wrapped function feq")
def feq(payload: dict):
    try:
        if feq is None:
            return {"success": False, "result": None, "error": "Function feq is not available"}
        result = feq(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="feq", description="Auto-wrapped function feq")
def feq(payload: dict):
    try:
        if feq is None:
            return {"success": False, "result": None, "error": "Function feq is not available"}
        result = feq(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)