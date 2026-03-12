import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from december-measurements.validators import check_root_only, check_empty
from december-measurements.CommunityCentricMeasurements import CommunityCentricMeasurements
from december-measurements.cascade_measurements import SingleCascadeMeasurements, igraph_from_pandas_edgelist, CascadeCollectionMeasurements, Cascade, get_original_tweet_ratio, igraph_add_edges_to_existing_graph
from december-measurements.ContentCentricMeasurements import ContentCentricMeasurements
from december-measurements.network_measurements import NetworkMeasurements, GithubNetworkMeasurements

mcp = FastMCP("unknown_service")


@mcp.tool(name="check_empty", description="Auto-wrapped function check_empty")
def check_empty(payload: dict):
    try:
        if check_empty is None:
            return {"success": False, "result": None, "error": "Function check_empty is not available"}
        result = check_empty(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="check_root_only", description="Auto-wrapped function check_root_only")
def check_root_only(payload: dict):
    try:
        if check_root_only is None:
            return {"success": False, "result": None, "error": "Function check_root_only is not available"}
        result = check_root_only(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="communitycentricmeasurements", description="CommunityCentricMeasurements class")
def communitycentricmeasurements(*args, **kwargs):
    """CommunityCentricMeasurements class"""
    try:
        if CommunityCentricMeasurements is None:
            return {"success": False, "result": None, "error": "Class CommunityCentricMeasurements is not available, path may need adjustment"}
        
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
        
        instance = CommunityCentricMeasurements(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="get_original_tweet_ratio", description="Auto-wrapped function get_original_tweet_ratio")
def get_original_tweet_ratio(payload: dict):
    try:
        if get_original_tweet_ratio is None:
            return {"success": False, "result": None, "error": "Function get_original_tweet_ratio is not available"}
        result = get_original_tweet_ratio(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="igraph_add_edges_to_existing_graph", description="Auto-wrapped function igraph_add_edges_to_existing_graph")
def igraph_add_edges_to_existing_graph(payload: dict):
    try:
        if igraph_add_edges_to_existing_graph is None:
            return {"success": False, "result": None, "error": "Function igraph_add_edges_to_existing_graph is not available"}
        result = igraph_add_edges_to_existing_graph(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="igraph_from_pandas_edgelist", description="Auto-wrapped function igraph_from_pandas_edgelist")
def igraph_from_pandas_edgelist(payload: dict):
    try:
        if igraph_from_pandas_edgelist is None:
            return {"success": False, "result": None, "error": "Function igraph_from_pandas_edgelist is not available"}
        result = igraph_from_pandas_edgelist(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="cascade", description="Cascade class")
def cascade(*args, **kwargs):
    """Cascade class"""
    try:
        if Cascade is None:
            return {"success": False, "result": None, "error": "Class Cascade is not available, path may need adjustment"}
        
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
        
        instance = Cascade(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="cascadecollectionmeasurements", description="CascadeCollectionMeasurements class")
def cascadecollectionmeasurements(*args, **kwargs):
    """CascadeCollectionMeasurements class"""
    try:
        if CascadeCollectionMeasurements is None:
            return {"success": False, "result": None, "error": "Class CascadeCollectionMeasurements is not available, path may need adjustment"}
        
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
        
        instance = CascadeCollectionMeasurements(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="singlecascademeasurements", description="SingleCascadeMeasurements class")
def singlecascademeasurements(*args, **kwargs):
    """SingleCascadeMeasurements class"""
    try:
        if SingleCascadeMeasurements is None:
            return {"success": False, "result": None, "error": "Class SingleCascadeMeasurements is not available, path may need adjustment"}
        
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
        
        instance = SingleCascadeMeasurements(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="contentcentricmeasurements", description="ContentCentricMeasurements class")
def contentcentricmeasurements(*args, **kwargs):
    """ContentCentricMeasurements class"""
    try:
        if ContentCentricMeasurements is None:
            return {"success": False, "result": None, "error": "Class ContentCentricMeasurements is not available, path may need adjustment"}
        
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
        
        instance = ContentCentricMeasurements(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="githubnetworkmeasurements", description="GithubNetworkMeasurements class")
def githubnetworkmeasurements(*args, **kwargs):
    """GithubNetworkMeasurements class"""
    try:
        if GithubNetworkMeasurements is None:
            return {"success": False, "result": None, "error": "Class GithubNetworkMeasurements is not available, path may need adjustment"}
        
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
        
        instance = GithubNetworkMeasurements(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="networkmeasurements", description="NetworkMeasurements class")
def networkmeasurements(*args, **kwargs):
    """NetworkMeasurements class"""
    try:
        if NetworkMeasurements is None:
            return {"success": False, "result": None, "error": "Class NetworkMeasurements is not available, path may need adjustment"}
        
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
        
        instance = NetworkMeasurements(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)