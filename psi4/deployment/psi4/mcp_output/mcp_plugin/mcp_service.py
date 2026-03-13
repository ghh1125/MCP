import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from conda.psi4-path-advisor import conda_info, compiler_type, compute_width, PreserveWhiteSpaceWrapRawTextHelpFormatter
from conda._conda_vers import version_func
from psi4.share.psi4.scripts.test_threading import run_psithon_inputs, print_math_ldd
from psi4.share.psi4.scripts.apply_license import check_header
from psi4.share.psi4.scripts.vmd_cube import call_montage, find_cubes, find_vmd
from psi4.share.psi4.basis.primitives.diff_gbs import bas_sanitize

mcp = FastMCP("unknown_service")


@mcp.tool(name="compiler_type", description="Auto-wrapped function compiler_type")
def compiler_type(payload: dict):
    try:
        if compiler_type is None:
            return {"success": False, "result": None, "error": "Function compiler_type is not available"}
        result = compiler_type(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="compute_width", description="Auto-wrapped function compute_width")
def compute_width(payload: dict):
    try:
        if compute_width is None:
            return {"success": False, "result": None, "error": "Function compute_width is not available"}
        result = compute_width(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="conda_info", description="Auto-wrapped function conda_info")
def conda_info(payload: dict):
    try:
        if conda_info is None:
            return {"success": False, "result": None, "error": "Function conda_info is not available"}
        result = conda_info(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="preservewhitespacewraprawtexthelpformatter", description="PreserveWhiteSpaceWrapRawTextHelpFormatter class")
def preservewhitespacewraprawtexthelpformatter(*args, **kwargs):
    """PreserveWhiteSpaceWrapRawTextHelpFormatter class"""
    try:
        if PreserveWhiteSpaceWrapRawTextHelpFormatter is None:
            return {"success": False, "result": None, "error": "Class PreserveWhiteSpaceWrapRawTextHelpFormatter is not available, path may need adjustment"}
        
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
        
        instance = PreserveWhiteSpaceWrapRawTextHelpFormatter(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="version_func", description="Auto-wrapped function version_func")
def version_func(payload: dict):
    try:
        if version_func is None:
            return {"success": False, "result": None, "error": "Function version_func is not available"}
        result = version_func(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="print_math_ldd", description="Auto-wrapped function print_math_ldd")
def print_math_ldd(payload: dict):
    try:
        if print_math_ldd is None:
            return {"success": False, "result": None, "error": "Function print_math_ldd is not available"}
        result = print_math_ldd(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="run_psithon_inputs", description="Auto-wrapped function run_psithon_inputs")
def run_psithon_inputs(payload: dict):
    try:
        if run_psithon_inputs is None:
            return {"success": False, "result": None, "error": "Function run_psithon_inputs is not available"}
        result = run_psithon_inputs(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="check_header", description="Auto-wrapped function check_header")
def check_header(payload: dict):
    try:
        if check_header is None:
            return {"success": False, "result": None, "error": "Function check_header is not available"}
        result = check_header(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="call_montage", description="Auto-wrapped function call_montage")
def call_montage(payload: dict):
    try:
        if call_montage is None:
            return {"success": False, "result": None, "error": "Function call_montage is not available"}
        result = call_montage(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="find_cubes", description="Auto-wrapped function find_cubes")
def find_cubes(payload: dict):
    try:
        if find_cubes is None:
            return {"success": False, "result": None, "error": "Function find_cubes is not available"}
        result = find_cubes(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="find_vmd", description="Auto-wrapped function find_vmd")
def find_vmd(payload: dict):
    try:
        if find_vmd is None:
            return {"success": False, "result": None, "error": "Function find_vmd is not available"}
        result = find_vmd(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="bas_sanitize", description="Auto-wrapped function bas_sanitize")
def bas_sanitize(payload: dict):
    try:
        if bas_sanitize is None:
            return {"success": False, "result": None, "error": "Function bas_sanitize is not available"}
        result = bas_sanitize(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)