import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from bin.benchmark_pydy_code_gen import run_benchmark
from bin.compare_linear_systems_solvers import numpy_umath_linalg_solve, scipy_linalg_solve, scipy_linalg_lapack_dposv
from examples.parallel-execution.joblib_demo import rhs_wrapper, odeint_wrapper
from examples.parallel-execution.multiprocessing_demo import rhs_wrapper, odeint_wrapper
from examples.Kane1985.Chapter6.util import PartialVelocity, generalized_active_forces_K, function_from_partials, generalized_active_forces

mcp = FastMCP("unknown_service")


@mcp.tool(name="run_benchmark", description="Auto-wrapped function run_benchmark")
def run_benchmark(payload: dict):
    try:
        if run_benchmark is None:
            return {"success": False, "result": None, "error": "Function run_benchmark is not available"}
        result = run_benchmark(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="numpy_umath_linalg_solve", description="Auto-wrapped function numpy_umath_linalg_solve")
def numpy_umath_linalg_solve(payload: dict):
    try:
        if numpy_umath_linalg_solve is None:
            return {"success": False, "result": None, "error": "Function numpy_umath_linalg_solve is not available"}
        result = numpy_umath_linalg_solve(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="scipy_linalg_lapack_dposv", description="Auto-wrapped function scipy_linalg_lapack_dposv")
def scipy_linalg_lapack_dposv(payload: dict):
    try:
        if scipy_linalg_lapack_dposv is None:
            return {"success": False, "result": None, "error": "Function scipy_linalg_lapack_dposv is not available"}
        result = scipy_linalg_lapack_dposv(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="scipy_linalg_solve", description="Auto-wrapped function scipy_linalg_solve")
def scipy_linalg_solve(payload: dict):
    try:
        if scipy_linalg_solve is None:
            return {"success": False, "result": None, "error": "Function scipy_linalg_solve is not available"}
        result = scipy_linalg_solve(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="odeint_wrapper", description="Auto-wrapped function odeint_wrapper")
def odeint_wrapper(payload: dict):
    try:
        if odeint_wrapper is None:
            return {"success": False, "result": None, "error": "Function odeint_wrapper is not available"}
        result = odeint_wrapper(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="rhs_wrapper", description="Auto-wrapped function rhs_wrapper")
def rhs_wrapper(payload: dict):
    try:
        if rhs_wrapper is None:
            return {"success": False, "result": None, "error": "Function rhs_wrapper is not available"}
        result = rhs_wrapper(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="odeint_wrapper", description="Auto-wrapped function odeint_wrapper")
def odeint_wrapper(payload: dict):
    try:
        if odeint_wrapper is None:
            return {"success": False, "result": None, "error": "Function odeint_wrapper is not available"}
        result = odeint_wrapper(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="rhs_wrapper", description="Auto-wrapped function rhs_wrapper")
def rhs_wrapper(payload: dict):
    try:
        if rhs_wrapper is None:
            return {"success": False, "result": None, "error": "Function rhs_wrapper is not available"}
        result = rhs_wrapper(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="function_from_partials", description="Auto-wrapped function function_from_partials")
def function_from_partials(payload: dict):
    try:
        if function_from_partials is None:
            return {"success": False, "result": None, "error": "Function function_from_partials is not available"}
        result = function_from_partials(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="generalized_active_forces", description="Auto-wrapped function generalized_active_forces")
def generalized_active_forces(payload: dict):
    try:
        if generalized_active_forces is None:
            return {"success": False, "result": None, "error": "Function generalized_active_forces is not available"}
        result = generalized_active_forces(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="generalized_active_forces_K", description="Auto-wrapped function generalized_active_forces_K")
def generalized_active_forces_K(payload: dict):
    try:
        if generalized_active_forces_K is None:
            return {"success": False, "result": None, "error": "Function generalized_active_forces_K is not available"}
        result = generalized_active_forces_K(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="partialvelocity", description="PartialVelocity class")
def partialvelocity(*args, **kwargs):
    """PartialVelocity class"""
    try:
        if PartialVelocity is None:
            return {"success": False, "result": None, "error": "Class PartialVelocity is not available, path may need adjustment"}
        
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
        
        instance = PartialVelocity(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)