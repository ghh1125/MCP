import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from setup import build_py
from doc.images import setup
from doc.ext import setup, git_role
from doc.ase.thermochemistry import output_to_string
from doc.ase.transport.transport_setup import pos
from doc.ase.dft.dos import MyCalc
from doc.ase.dft.bz import plot, bz_vertices
from doc.ase.build.surface import save
from doc.tutorials.ga.ga_basic_parameters import combine_parameters, jtg

mcp = FastMCP("unknown_service")


@mcp.tool(name="build_py", description="build_py class")
def build_py(*args, **kwargs):
    """build_py class"""
    try:
        if build_py is None:
            return {"success": False, "result": None, "error": "Class build_py is not available, path may need adjustment"}
        
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
        
        instance = build_py(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="setup", description="Auto-wrapped function setup")
def setup(payload: dict):
    try:
        if setup is None:
            return {"success": False, "result": None, "error": "Function setup is not available"}
        result = setup(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="git_role", description="Auto-wrapped function git_role")
def git_role(payload: dict):
    try:
        if git_role is None:
            return {"success": False, "result": None, "error": "Function git_role is not available"}
        result = git_role(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="setup", description="Auto-wrapped function setup")
def setup(payload: dict):
    try:
        if setup is None:
            return {"success": False, "result": None, "error": "Function setup is not available"}
        result = setup(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="output_to_string", description="Auto-wrapped function output_to_string")
def output_to_string(payload: dict):
    try:
        if output_to_string is None:
            return {"success": False, "result": None, "error": "Function output_to_string is not available"}
        result = output_to_string(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="pos", description="Auto-wrapped function pos")
def pos(payload: dict):
    try:
        if pos is None:
            return {"success": False, "result": None, "error": "Function pos is not available"}
        result = pos(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="mycalc", description="MyCalc class")
def mycalc(*args, **kwargs):
    """MyCalc class"""
    try:
        if MyCalc is None:
            return {"success": False, "result": None, "error": "Class MyCalc is not available, path may need adjustment"}
        
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
        
        instance = MyCalc(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="bz_vertices", description="Auto-wrapped function bz_vertices")
def bz_vertices(payload: dict):
    try:
        if bz_vertices is None:
            return {"success": False, "result": None, "error": "Function bz_vertices is not available"}
        result = bz_vertices(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="plot", description="Auto-wrapped function plot")
def plot(payload: dict):
    try:
        if plot is None:
            return {"success": False, "result": None, "error": "Function plot is not available"}
        result = plot(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="save", description="Auto-wrapped function save")
def save(payload: dict):
    try:
        if save is None:
            return {"success": False, "result": None, "error": "Function save is not available"}
        result = save(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="combine_parameters", description="Auto-wrapped function combine_parameters")
def combine_parameters(payload: dict):
    try:
        if combine_parameters is None:
            return {"success": False, "result": None, "error": "Function combine_parameters is not available"}
        result = combine_parameters(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="jtg", description="Auto-wrapped function jtg")
def jtg(payload: dict):
    try:
        if jtg is None:
            return {"success": False, "result": None, "error": "Function jtg is not available"}
        result = jtg(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)