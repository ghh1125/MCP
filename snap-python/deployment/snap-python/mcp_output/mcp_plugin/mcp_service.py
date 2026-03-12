import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from setup import SwigExtension, SwigBuild
from swig.setup import SwigExtension, PkgBuild
from swig.gen.disp-custom import ConvertGraph, ConvertSubGraph, ConvertESubGraph
from swig.gen.genClassFn.archive.genClassFnExt import removeFirstParam, genFuncCall, getFuncName
from dev.examples.tneanet-cpp import main
from dev.examples.snapswig-check import main

mcp = FastMCP("unknown_service")


@mcp.tool(name="swigbuild", description="SwigBuild class")
def swigbuild(*args, **kwargs):
    """SwigBuild class"""
    try:
        if SwigBuild is None:
            return {"success": False, "result": None, "error": "Class SwigBuild is not available, path may need adjustment"}
        
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
        
        instance = SwigBuild(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="swigextension", description="SwigExtension class")
def swigextension(*args, **kwargs):
    """SwigExtension class"""
    try:
        if SwigExtension is None:
            return {"success": False, "result": None, "error": "Class SwigExtension is not available, path may need adjustment"}
        
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
        
        instance = SwigExtension(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="pkgbuild", description="PkgBuild class")
def pkgbuild(*args, **kwargs):
    """PkgBuild class"""
    try:
        if PkgBuild is None:
            return {"success": False, "result": None, "error": "Class PkgBuild is not available, path may need adjustment"}
        
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
        
        instance = PkgBuild(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="swigextension", description="SwigExtension class")
def swigextension(*args, **kwargs):
    """SwigExtension class"""
    try:
        if SwigExtension is None:
            return {"success": False, "result": None, "error": "Class SwigExtension is not available, path may need adjustment"}
        
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
        
        instance = SwigExtension(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ConvertESubGraph", description="Auto-wrapped function ConvertESubGraph")
def ConvertESubGraph(payload: dict):
    try:
        if ConvertESubGraph is None:
            return {"success": False, "result": None, "error": "Function ConvertESubGraph is not available"}
        result = ConvertESubGraph(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ConvertGraph", description="Auto-wrapped function ConvertGraph")
def ConvertGraph(payload: dict):
    try:
        if ConvertGraph is None:
            return {"success": False, "result": None, "error": "Function ConvertGraph is not available"}
        result = ConvertGraph(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ConvertSubGraph", description="Auto-wrapped function ConvertSubGraph")
def ConvertSubGraph(payload: dict):
    try:
        if ConvertSubGraph is None:
            return {"success": False, "result": None, "error": "Function ConvertSubGraph is not available"}
        result = ConvertSubGraph(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="genFuncCall", description="Auto-wrapped function genFuncCall")
def genFuncCall(payload: dict):
    try:
        if genFuncCall is None:
            return {"success": False, "result": None, "error": "Function genFuncCall is not available"}
        result = genFuncCall(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="getFuncName", description="Auto-wrapped function getFuncName")
def getFuncName(payload: dict):
    try:
        if getFuncName is None:
            return {"success": False, "result": None, "error": "Function getFuncName is not available"}
        result = getFuncName(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="removeFirstParam", description="Auto-wrapped function removeFirstParam")
def removeFirstParam(payload: dict):
    try:
        if removeFirstParam is None:
            return {"success": False, "result": None, "error": "Function removeFirstParam is not available"}
        result = removeFirstParam(**payload)
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

@mcp.tool(name="main", description="Auto-wrapped function main")
def main(payload: dict):
    try:
        if main is None:
            return {"success": False, "result": None, "error": "Function main is not available"}
        result = main(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)