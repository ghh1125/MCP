import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from datasets.construct_pdbbind_df import construct_df, extract_labels
from docs.source.conf import linkcode_resolve
from contrib.visualization.utils import combine_mdtraj, display_images, convert_lines_to_mdtraj
from contrib.DeepMHC.bd13_datasets import load_bd2013_human, to_one_hot_array, featurize
from contrib.DeepMHC.deepmhc import DeepMHC
from contrib.dragonn.models import MotifScoreRNN, gkmSVM

mcp = FastMCP("unknown_service")


@mcp.tool(name="construct_df", description="Auto-wrapped function construct_df")
def construct_df(payload: dict):
    try:
        if construct_df is None:
            return {"success": False, "result": None, "error": "Function construct_df is not available"}
        result = construct_df(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="extract_labels", description="Auto-wrapped function extract_labels")
def extract_labels(payload: dict):
    try:
        if extract_labels is None:
            return {"success": False, "result": None, "error": "Function extract_labels is not available"}
        result = extract_labels(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="linkcode_resolve", description="Auto-wrapped function linkcode_resolve")
def linkcode_resolve(payload: dict):
    try:
        if linkcode_resolve is None:
            return {"success": False, "result": None, "error": "Function linkcode_resolve is not available"}
        result = linkcode_resolve(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="combine_mdtraj", description="Auto-wrapped function combine_mdtraj")
def combine_mdtraj(payload: dict):
    try:
        if combine_mdtraj is None:
            return {"success": False, "result": None, "error": "Function combine_mdtraj is not available"}
        result = combine_mdtraj(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="convert_lines_to_mdtraj", description="Auto-wrapped function convert_lines_to_mdtraj")
def convert_lines_to_mdtraj(payload: dict):
    try:
        if convert_lines_to_mdtraj is None:
            return {"success": False, "result": None, "error": "Function convert_lines_to_mdtraj is not available"}
        result = convert_lines_to_mdtraj(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="display_images", description="Auto-wrapped function display_images")
def display_images(payload: dict):
    try:
        if display_images is None:
            return {"success": False, "result": None, "error": "Function display_images is not available"}
        result = display_images(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="featurize", description="Auto-wrapped function featurize")
def featurize(payload: dict):
    try:
        if featurize is None:
            return {"success": False, "result": None, "error": "Function featurize is not available"}
        result = featurize(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="load_bd2013_human", description="Auto-wrapped function load_bd2013_human")
def load_bd2013_human(payload: dict):
    try:
        if load_bd2013_human is None:
            return {"success": False, "result": None, "error": "Function load_bd2013_human is not available"}
        result = load_bd2013_human(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="to_one_hot_array", description="Auto-wrapped function to_one_hot_array")
def to_one_hot_array(payload: dict):
    try:
        if to_one_hot_array is None:
            return {"success": False, "result": None, "error": "Function to_one_hot_array is not available"}
        result = to_one_hot_array(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="deepmhc", description="DeepMHC class")
def deepmhc(*args, **kwargs):
    """DeepMHC class"""
    try:
        if DeepMHC is None:
            return {"success": False, "result": None, "error": "Class DeepMHC is not available, path may need adjustment"}
        
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
        
        instance = DeepMHC(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="motifscorernn", description="MotifScoreRNN class")
def motifscorernn(*args, **kwargs):
    """MotifScoreRNN class"""
    try:
        if MotifScoreRNN is None:
            return {"success": False, "result": None, "error": "Class MotifScoreRNN is not available, path may need adjustment"}
        
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
        
        instance = MotifScoreRNN(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="gkmsvm", description="gkmSVM class")
def gkmsvm(*args, **kwargs):
    """gkmSVM class"""
    try:
        if gkmSVM is None:
            return {"success": False, "result": None, "error": "Class gkmSVM is not available, path may need adjustment"}
        
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
        
        instance = gkmSVM(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)