import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from ephem import Ariel, holiday, AlwaysUpError, Callisto, city, describe_riset_search
from ephem.stars import star
from ephem.cities import city

mcp = FastMCP("unknown_service")


@mcp.tool(name="city", description="Auto-wrapped function city")
def city(payload: dict):
    try:
        if city is None:
            return {"success": False, "result": None, "error": "Function city is not available"}
        result = city(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="describe_riset_search", description="Auto-wrapped function describe_riset_search")
def describe_riset_search(payload: dict):
    try:
        if describe_riset_search is None:
            return {"success": False, "result": None, "error": "Function describe_riset_search is not available"}
        result = describe_riset_search(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="holiday", description="Auto-wrapped function holiday")
def holiday(payload: dict):
    try:
        if holiday is None:
            return {"success": False, "result": None, "error": "Function holiday is not available"}
        result = holiday(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="alwaysuperror", description="AlwaysUpError class")
def alwaysuperror(*args, **kwargs):
    """AlwaysUpError class"""
    try:
        if AlwaysUpError is None:
            return {"success": False, "result": None, "error": "Class AlwaysUpError is not available, path may need adjustment"}
        
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
        
        instance = AlwaysUpError(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ariel", description="Ariel class")
def ariel(*args, **kwargs):
    """Ariel class"""
    try:
        if Ariel is None:
            return {"success": False, "result": None, "error": "Class Ariel is not available, path may need adjustment"}
        
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
        
        instance = Ariel(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="callisto", description="Callisto class")
def callisto(*args, **kwargs):
    """Callisto class"""
    try:
        if Callisto is None:
            return {"success": False, "result": None, "error": "Class Callisto is not available, path may need adjustment"}
        
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
        
        instance = Callisto(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="star", description="Auto-wrapped function star")
def star(payload: dict):
    try:
        if star is None:
            return {"success": False, "result": None, "error": "Function star is not available"}
        result = star(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="city", description="Auto-wrapped function city")
def city(payload: dict):
    try:
        if city is None:
            return {"success": False, "result": None, "error": "Function city is not available"}
        result = city(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)