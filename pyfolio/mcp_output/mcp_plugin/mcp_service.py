import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from versioneer import get_cmdclass, VersioneerBadRootError, do_setup, do_vcs_install, VersioneerConfig, NotThisMethod

mcp = FastMCP("unknown_service")


@mcp.tool(name="do_setup", description="Auto-wrapped function do_setup")
def do_setup(payload: dict):
    try:
        if do_setup is None:
            return {"success": False, "result": None, "error": "Function do_setup is not available"}
        result = do_setup(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="do_vcs_install", description="Auto-wrapped function do_vcs_install")
def do_vcs_install(payload: dict):
    try:
        if do_vcs_install is None:
            return {"success": False, "result": None, "error": "Function do_vcs_install is not available"}
        result = do_vcs_install(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_cmdclass", description="Auto-wrapped function get_cmdclass")
def get_cmdclass(payload: dict):
    try:
        if get_cmdclass is None:
            return {"success": False, "result": None, "error": "Function get_cmdclass is not available"}
        result = get_cmdclass(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="notthismethod", description="NotThisMethod class")
def notthismethod(*args, **kwargs):
    """NotThisMethod class"""
    try:
        if NotThisMethod is None:
            return {"success": False, "result": None, "error": "Class NotThisMethod is not available, path may need adjustment"}
        
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
        
        instance = NotThisMethod(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="versioneerbadrooterror", description="VersioneerBadRootError class")
def versioneerbadrooterror(*args, **kwargs):
    """VersioneerBadRootError class"""
    try:
        if VersioneerBadRootError is None:
            return {"success": False, "result": None, "error": "Class VersioneerBadRootError is not available, path may need adjustment"}
        
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
        
        instance = VersioneerBadRootError(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="versioneerconfig", description="VersioneerConfig class")
def versioneerconfig(*args, **kwargs):
    """VersioneerConfig class"""
    try:
        if VersioneerConfig is None:
            return {"success": False, "result": None, "error": "Class VersioneerConfig is not available, path may need adjustment"}
        
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
        
        instance = VersioneerConfig(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)