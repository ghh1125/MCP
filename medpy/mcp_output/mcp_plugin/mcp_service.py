import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from setup import run_setup, read, ve_build_ext, try_find_library, BuildFailed
from bin.medpy_reslice_3d_to_4d import main, getArguments, getParser
from bin.medpy_extract_min_max import main, getArguments, getParser
from bin.medpy_convert import getArguments

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

@mcp.tool(name="run_setup", description="Auto-wrapped function run_setup")
def run_setup(payload: dict):
    try:
        if run_setup is None:
            return {"success": False, "result": None, "error": "Function run_setup is not available"}
        result = run_setup(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="try_find_library", description="Auto-wrapped function try_find_library")
def try_find_library(payload: dict):
    try:
        if try_find_library is None:
            return {"success": False, "result": None, "error": "Function try_find_library is not available"}
        result = try_find_library(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="buildfailed", description="BuildFailed class")
def buildfailed(*args, **kwargs):
    """BuildFailed class"""
    try:
        if BuildFailed is None:
            return {"success": False, "result": None, "error": "Class BuildFailed is not available, path may need adjustment"}
        
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
        
        instance = BuildFailed(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ve_build_ext", description="ve_build_ext class")
def ve_build_ext(*args, **kwargs):
    """ve_build_ext class"""
    try:
        if ve_build_ext is None:
            return {"success": False, "result": None, "error": "Class ve_build_ext is not available, path may need adjustment"}
        
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
        
        instance = ve_build_ext(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="getArguments", description="Auto-wrapped function getArguments")
def getArguments(payload: dict):
    try:
        if getArguments is None:
            return {"success": False, "result": None, "error": "Function getArguments is not available"}
        result = getArguments(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="getParser", description="Auto-wrapped function getParser")
def getParser(payload: dict):
    try:
        if getParser is None:
            return {"success": False, "result": None, "error": "Function getParser is not available"}
        result = getParser(**payload)
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

@mcp.tool(name="getArguments", description="Auto-wrapped function getArguments")
def getArguments(payload: dict):
    try:
        if getArguments is None:
            return {"success": False, "result": None, "error": "Function getArguments is not available"}
        result = getArguments(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="getParser", description="Auto-wrapped function getParser")
def getParser(payload: dict):
    try:
        if getParser is None:
            return {"success": False, "result": None, "error": "Function getParser is not available"}
        result = getParser(**payload)
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

@mcp.tool(name="getArguments", description="Auto-wrapped function getArguments")
def getArguments(payload: dict):
    try:
        if getArguments is None:
            return {"success": False, "result": None, "error": "Function getArguments is not available"}
        result = getArguments(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)