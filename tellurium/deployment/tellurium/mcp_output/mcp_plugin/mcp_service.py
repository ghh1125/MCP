import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from docs.conf import Mock
from examples.tellurium-files.events import onEventTrigger, onEvent, onEventAssignment
from scripts.download_count import parse_release_json, get_git_releases_json, plot_release_df

mcp = FastMCP("unknown_service")


@mcp.tool(name="mock", description="Mock class")
def mock(*args, **kwargs):
    """Mock class"""
    try:
        if Mock is None:
            return {"success": False, "result": None, "error": "Class Mock is not available, path may need adjustment"}
        
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
        
        instance = Mock(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="onEvent", description="Auto-wrapped function onEvent")
def onEvent(payload: dict):
    try:
        if onEvent is None:
            return {"success": False, "result": None, "error": "Function onEvent is not available"}
        result = onEvent(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="onEventAssignment", description="Auto-wrapped function onEventAssignment")
def onEventAssignment(payload: dict):
    try:
        if onEventAssignment is None:
            return {"success": False, "result": None, "error": "Function onEventAssignment is not available"}
        result = onEventAssignment(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="onEventTrigger", description="Auto-wrapped function onEventTrigger")
def onEventTrigger(payload: dict):
    try:
        if onEventTrigger is None:
            return {"success": False, "result": None, "error": "Function onEventTrigger is not available"}
        result = onEventTrigger(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_git_releases_json", description="Auto-wrapped function get_git_releases_json")
def get_git_releases_json(payload: dict):
    try:
        if get_git_releases_json is None:
            return {"success": False, "result": None, "error": "Function get_git_releases_json is not available"}
        result = get_git_releases_json(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_release_json", description="Auto-wrapped function parse_release_json")
def parse_release_json(payload: dict):
    try:
        if parse_release_json is None:
            return {"success": False, "result": None, "error": "Function parse_release_json is not available"}
        result = parse_release_json(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="plot_release_df", description="Auto-wrapped function plot_release_df")
def plot_release_df(payload: dict):
    try:
        if plot_release_df is None:
            return {"success": False, "result": None, "error": "Function plot_release_df is not available"}
        result = plot_release_df(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)