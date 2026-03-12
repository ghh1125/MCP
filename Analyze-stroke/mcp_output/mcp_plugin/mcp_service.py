import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from dim_reduction import DimensionAnalyzer
from feature_selection import FeatureSelectionAnalyzer
from models import ModelManager
from data_loader import DataLoader
from test_env import check_environment
from causal_module import CausalAnalyzer
from plot_utils import draw_effect_chart, draw_pvalue_chart, add_offset_labels
from main import main, DualLogger
from run_all_causal import parse_log_output

mcp = FastMCP("unknown_service")


@mcp.tool(name="dimensionanalyzer", description="DimensionAnalyzer class")
def dimensionanalyzer(*args, **kwargs):
    """DimensionAnalyzer class"""
    try:
        if DimensionAnalyzer is None:
            return {"success": False, "result": None, "error": "Class DimensionAnalyzer is not available, path may need adjustment"}
        
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
        
        instance = DimensionAnalyzer(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="featureselectionanalyzer", description="FeatureSelectionAnalyzer class")
def featureselectionanalyzer(*args, **kwargs):
    """FeatureSelectionAnalyzer class"""
    try:
        if FeatureSelectionAnalyzer is None:
            return {"success": False, "result": None, "error": "Class FeatureSelectionAnalyzer is not available, path may need adjustment"}
        
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
        
        instance = FeatureSelectionAnalyzer(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="modelmanager", description="ModelManager class")
def modelmanager(*args, **kwargs):
    """ModelManager class"""
    try:
        if ModelManager is None:
            return {"success": False, "result": None, "error": "Class ModelManager is not available, path may need adjustment"}
        
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
        
        instance = ModelManager(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="dataloader", description="DataLoader class")
def dataloader(*args, **kwargs):
    """DataLoader class"""
    try:
        if DataLoader is None:
            return {"success": False, "result": None, "error": "Class DataLoader is not available, path may need adjustment"}
        
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
        
        instance = DataLoader(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="check_environment", description="Auto-wrapped function check_environment")
def check_environment(payload: dict):
    try:
        if check_environment is None:
            return {"success": False, "result": None, "error": "Function check_environment is not available"}
        result = check_environment(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="causalanalyzer", description="CausalAnalyzer class")
def causalanalyzer(*args, **kwargs):
    """CausalAnalyzer class"""
    try:
        if CausalAnalyzer is None:
            return {"success": False, "result": None, "error": "Class CausalAnalyzer is not available, path may need adjustment"}
        
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
        
        instance = CausalAnalyzer(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="add_offset_labels", description="Auto-wrapped function add_offset_labels")
def add_offset_labels(payload: dict):
    try:
        if add_offset_labels is None:
            return {"success": False, "result": None, "error": "Function add_offset_labels is not available"}
        result = add_offset_labels(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="draw_effect_chart", description="Auto-wrapped function draw_effect_chart")
def draw_effect_chart(payload: dict):
    try:
        if draw_effect_chart is None:
            return {"success": False, "result": None, "error": "Function draw_effect_chart is not available"}
        result = draw_effect_chart(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="draw_pvalue_chart", description="Auto-wrapped function draw_pvalue_chart")
def draw_pvalue_chart(payload: dict):
    try:
        if draw_pvalue_chart is None:
            return {"success": False, "result": None, "error": "Function draw_pvalue_chart is not available"}
        result = draw_pvalue_chart(**payload)
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

@mcp.tool(name="duallogger", description="DualLogger class")
def duallogger(*args, **kwargs):
    """DualLogger class"""
    try:
        if DualLogger is None:
            return {"success": False, "result": None, "error": "Class DualLogger is not available, path may need adjustment"}
        
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
        
        instance = DualLogger(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_log_output", description="Auto-wrapped function parse_log_output")
def parse_log_output(payload: dict):
    try:
        if parse_log_output is None:
            return {"success": False, "result": None, "error": "Function parse_log_output is not available"}
        result = parse_log_output(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)