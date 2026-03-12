import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from python.setup import BDistWheelABINone, BuildExtCommand, build_cmdstan_model, get_backends_from_env, BuildPyCommand, build_models
from python.scripts.generate_holidays_file import utf8_to_ascii, generate_holidays_df

mcp = FastMCP("unknown_service")


@mcp.tool(name="build_cmdstan_model", description="Auto-wrapped function build_cmdstan_model")
def build_cmdstan_model(payload: dict):
    try:
        if build_cmdstan_model is None:
            return {"success": False, "result": None, "error": "Function build_cmdstan_model is not available"}
        result = build_cmdstan_model(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="build_models", description="Auto-wrapped function build_models")
def build_models(payload: dict):
    try:
        if build_models is None:
            return {"success": False, "result": None, "error": "Function build_models is not available"}
        result = build_models(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_backends_from_env", description="Auto-wrapped function get_backends_from_env")
def get_backends_from_env(payload: dict):
    try:
        if get_backends_from_env is None:
            return {"success": False, "result": None, "error": "Function get_backends_from_env is not available"}
        result = get_backends_from_env(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="bdistwheelabinone", description="BDistWheelABINone class")
def bdistwheelabinone(*args, **kwargs):
    """BDistWheelABINone class"""
    try:
        if BDistWheelABINone is None:
            return {"success": False, "result": None, "error": "Class BDistWheelABINone is not available, path may need adjustment"}
        
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
        
        instance = BDistWheelABINone(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="buildextcommand", description="BuildExtCommand class")
def buildextcommand(*args, **kwargs):
    """BuildExtCommand class"""
    try:
        if BuildExtCommand is None:
            return {"success": False, "result": None, "error": "Class BuildExtCommand is not available, path may need adjustment"}
        
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
        
        instance = BuildExtCommand(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="buildpycommand", description="BuildPyCommand class")
def buildpycommand(*args, **kwargs):
    """BuildPyCommand class"""
    try:
        if BuildPyCommand is None:
            return {"success": False, "result": None, "error": "Class BuildPyCommand is not available, path may need adjustment"}
        
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
        
        instance = BuildPyCommand(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="generate_holidays_df", description="Auto-wrapped function generate_holidays_df")
def generate_holidays_df(payload: dict):
    try:
        if generate_holidays_df is None:
            return {"success": False, "result": None, "error": "Function generate_holidays_df is not available"}
        result = generate_holidays_df(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="utf8_to_ascii", description="Auto-wrapped function utf8_to_ascii")
def utf8_to_ascii(payload: dict):
    try:
        if utf8_to_ascii is None:
            return {"success": False, "result": None, "error": "Function utf8_to_ascii is not available"}
        result = utf8_to_ascii(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)