import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from generate.patch_readme import PatchReadme
from generate.patch_version_numbers import PatchVersionNumbers, Patch
from generate.checksum import Checksum
from generate.check_internal_links import FindBogusLinks, FindBrokenLinks
from generate.test import JplStateRecord, AngleDiff, ArcminPosError, BaryStateFunc, HelioStateFunc, Aberration

mcp = FastMCP("unknown_service")


@mcp.tool(name="PatchReadme", description="Auto-wrapped function PatchReadme")
def PatchReadme(payload: dict):
    try:
        if PatchReadme is None:
            return {"success": False, "result": None, "error": "Function PatchReadme is not available"}
        result = PatchReadme(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="Patch", description="Auto-wrapped function Patch")
def Patch(payload: dict):
    try:
        if Patch is None:
            return {"success": False, "result": None, "error": "Function Patch is not available"}
        result = Patch(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="PatchVersionNumbers", description="Auto-wrapped function PatchVersionNumbers")
def PatchVersionNumbers(payload: dict):
    try:
        if PatchVersionNumbers is None:
            return {"success": False, "result": None, "error": "Function PatchVersionNumbers is not available"}
        result = PatchVersionNumbers(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="Checksum", description="Auto-wrapped function Checksum")
def Checksum(payload: dict):
    try:
        if Checksum is None:
            return {"success": False, "result": None, "error": "Function Checksum is not available"}
        result = Checksum(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="FindBogusLinks", description="Auto-wrapped function FindBogusLinks")
def FindBogusLinks(payload: dict):
    try:
        if FindBogusLinks is None:
            return {"success": False, "result": None, "error": "Function FindBogusLinks is not available"}
        result = FindBogusLinks(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="FindBrokenLinks", description="Auto-wrapped function FindBrokenLinks")
def FindBrokenLinks(payload: dict):
    try:
        if FindBrokenLinks is None:
            return {"success": False, "result": None, "error": "Function FindBrokenLinks is not available"}
        result = FindBrokenLinks(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="Aberration", description="Auto-wrapped function Aberration")
def Aberration(payload: dict):
    try:
        if Aberration is None:
            return {"success": False, "result": None, "error": "Function Aberration is not available"}
        result = Aberration(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="AngleDiff", description="Auto-wrapped function AngleDiff")
def AngleDiff(payload: dict):
    try:
        if AngleDiff is None:
            return {"success": False, "result": None, "error": "Function AngleDiff is not available"}
        result = AngleDiff(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ArcminPosError", description="Auto-wrapped function ArcminPosError")
def ArcminPosError(payload: dict):
    try:
        if ArcminPosError is None:
            return {"success": False, "result": None, "error": "Function ArcminPosError is not available"}
        result = ArcminPosError(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="barystatefunc", description="BaryStateFunc class")
def barystatefunc(*args, **kwargs):
    """BaryStateFunc class"""
    try:
        if BaryStateFunc is None:
            return {"success": False, "result": None, "error": "Class BaryStateFunc is not available, path may need adjustment"}
        
        # MCP parameter type conversion
        converted_args = []
        converted_kwargs = kwargs.copy()
        
        # Handle position argument type conversion
        for arg in args:
            if isinstance(arg, str):
                # Try to convert to numeric type
                try:
                    if '.' in arg:
                        converted_args.append(float(arg))
                    else:
                        converted_args.append(int(arg))
                except ValueError:
                    converted_args.append(arg)
            else:
                converted_args.append(arg)
        
        # Handle keyword argument type conversion
        for key, value in converted_kwargs.items():
            if isinstance(value, str):
                try:
                    if '.' in value:
                        converted_kwargs[key] = float(value)
                    else:
                        converted_kwargs[key] = int(value)
                except ValueError:
                    pass
        
        instance = BaryStateFunc(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="heliostatefunc", description="HelioStateFunc class")
def heliostatefunc(*args, **kwargs):
    """HelioStateFunc class"""
    try:
        if HelioStateFunc is None:
            return {"success": False, "result": None, "error": "Class HelioStateFunc is not available, path may need adjustment"}
        
        # MCP parameter type conversion
        converted_args = []
        converted_kwargs = kwargs.copy()
        
        # Handle position argument type conversion
        for arg in args:
            if isinstance(arg, str):
                # Try to convert to numeric type
                try:
                    if '.' in arg:
                        converted_args.append(float(arg))
                    else:
                        converted_args.append(int(arg))
                except ValueError:
                    converted_args.append(arg)
            else:
                converted_args.append(arg)
        
        # Handle keyword argument type conversion
        for key, value in converted_kwargs.items():
            if isinstance(value, str):
                try:
                    if '.' in value:
                        converted_kwargs[key] = float(value)
                    else:
                        converted_kwargs[key] = int(value)
                except ValueError:
                    pass
        
        instance = HelioStateFunc(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="jplstaterecord", description="JplStateRecord class")
def jplstaterecord(*args, **kwargs):
    """JplStateRecord class"""
    try:
        if JplStateRecord is None:
            return {"success": False, "result": None, "error": "Class JplStateRecord is not available, path may need adjustment"}
        
        # MCP parameter type conversion
        converted_args = []
        converted_kwargs = kwargs.copy()
        
        # Handle position argument type conversion
        for arg in args:
            if isinstance(arg, str):
                # Try to convert to numeric type
                try:
                    if '.' in arg:
                        converted_args.append(float(arg))
                    else:
                        converted_args.append(int(arg))
                except ValueError:
                    converted_args.append(arg)
            else:
                converted_args.append(arg)
        
        # Handle keyword argument type conversion
        for key, value in converted_kwargs.items():
            if isinstance(value, str):
                try:
                    if '.' in value:
                        converted_kwargs[key] = float(value)
                    else:
                        converted_kwargs[key] = int(value)
                except ValueError:
                    pass
        
        instance = JplStateRecord(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)