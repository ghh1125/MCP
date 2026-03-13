import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from docs.generate_redirects import generate_redirects
from libs.langgraph.langgraph.config import get_stream_writer, get_store, get_config
from libs.langgraph.langgraph.warnings import LangGraphDeprecatedSinceV10, LangGraphDeprecatedSinceV11, LangGraphDeprecatedSinceV05
from libs.langgraph.langgraph.types import ensure_valid_checkpointer, CachePolicy, CheckpointPayload, CacheKey, interrupt

mcp = FastMCP("unknown_service")


@mcp.tool(name="generate_redirects", description="Auto-wrapped function generate_redirects")
def generate_redirects(payload: dict):
    try:
        if generate_redirects is None:
            return {"success": False, "result": None, "error": "Function generate_redirects is not available"}
        result = generate_redirects(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_config", description="Auto-wrapped function get_config")
def get_config(payload: dict):
    try:
        if get_config is None:
            return {"success": False, "result": None, "error": "Function get_config is not available"}
        result = get_config(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_store", description="Auto-wrapped function get_store")
def get_store(payload: dict):
    try:
        if get_store is None:
            return {"success": False, "result": None, "error": "Function get_store is not available"}
        result = get_store(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_stream_writer", description="Auto-wrapped function get_stream_writer")
def get_stream_writer(payload: dict):
    try:
        if get_stream_writer is None:
            return {"success": False, "result": None, "error": "Function get_stream_writer is not available"}
        result = get_stream_writer(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="langgraphdeprecatedsincev05", description="LangGraphDeprecatedSinceV05 class")
def langgraphdeprecatedsincev05(*args, **kwargs):
    """LangGraphDeprecatedSinceV05 class"""
    try:
        if LangGraphDeprecatedSinceV05 is None:
            return {"success": False, "result": None, "error": "Class LangGraphDeprecatedSinceV05 is not available, path may need adjustment"}
        
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
        
        instance = LangGraphDeprecatedSinceV05(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="langgraphdeprecatedsincev10", description="LangGraphDeprecatedSinceV10 class")
def langgraphdeprecatedsincev10(*args, **kwargs):
    """LangGraphDeprecatedSinceV10 class"""
    try:
        if LangGraphDeprecatedSinceV10 is None:
            return {"success": False, "result": None, "error": "Class LangGraphDeprecatedSinceV10 is not available, path may need adjustment"}
        
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
        
        instance = LangGraphDeprecatedSinceV10(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="langgraphdeprecatedsincev11", description="LangGraphDeprecatedSinceV11 class")
def langgraphdeprecatedsincev11(*args, **kwargs):
    """LangGraphDeprecatedSinceV11 class"""
    try:
        if LangGraphDeprecatedSinceV11 is None:
            return {"success": False, "result": None, "error": "Class LangGraphDeprecatedSinceV11 is not available, path may need adjustment"}
        
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
        
        instance = LangGraphDeprecatedSinceV11(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="ensure_valid_checkpointer", description="Auto-wrapped function ensure_valid_checkpointer")
def ensure_valid_checkpointer(payload: dict):
    try:
        if ensure_valid_checkpointer is None:
            return {"success": False, "result": None, "error": "Function ensure_valid_checkpointer is not available"}
        result = ensure_valid_checkpointer(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="interrupt", description="Auto-wrapped function interrupt")
def interrupt(payload: dict):
    try:
        if interrupt is None:
            return {"success": False, "result": None, "error": "Function interrupt is not available"}
        result = interrupt(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="cachekey", description="CacheKey class")
def cachekey(*args, **kwargs):
    """CacheKey class"""
    try:
        if CacheKey is None:
            return {"success": False, "result": None, "error": "Class CacheKey is not available, path may need adjustment"}
        
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
        
        instance = CacheKey(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="cachepolicy", description="CachePolicy class")
def cachepolicy(*args, **kwargs):
    """CachePolicy class"""
    try:
        if CachePolicy is None:
            return {"success": False, "result": None, "error": "Class CachePolicy is not available, path may need adjustment"}
        
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
        
        instance = CachePolicy(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="checkpointpayload", description="CheckpointPayload class")
def checkpointpayload(*args, **kwargs):
    """CheckpointPayload class"""
    try:
        if CheckpointPayload is None:
            return {"success": False, "result": None, "error": "Class CheckpointPayload is not available, path may need adjustment"}
        
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
        
        instance = CheckpointPayload(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)