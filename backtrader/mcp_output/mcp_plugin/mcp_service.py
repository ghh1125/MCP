import os
import sys

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from tools.rewrite-data import parse_args, runstrat
from tools.yahoodownload import parse_args, YahooDownload
from contrib.utils.iqfeed-to-influxdb import IQFeedTool
from contrib.utils.influxdb-import import InfluxDBTool
from contrib.samples.pair-trading import runstrategy, parse_args, PairTradingStrategy
from samples.weekdays-filler.weekdaysfiller import WeekDaysFiller
from samples.weekdays-filler.weekdaysaligner import parse_args, runstrat

mcp = FastMCP("unknown_service")


@mcp.tool(name="parse_args", description="Auto-wrapped function parse_args")
def parse_args(payload: dict):
    try:
        if parse_args is None:
            return {"success": False, "result": None, "error": "Function parse_args is not available"}
        result = parse_args(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="runstrat", description="Auto-wrapped function runstrat")
def runstrat(payload: dict):
    try:
        if runstrat is None:
            return {"success": False, "result": None, "error": "Function runstrat is not available"}
        result = runstrat(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_args", description="Auto-wrapped function parse_args")
def parse_args(payload: dict):
    try:
        if parse_args is None:
            return {"success": False, "result": None, "error": "Function parse_args is not available"}
        result = parse_args(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="yahoodownload", description="YahooDownload class")
def yahoodownload(*args, **kwargs):
    """YahooDownload class"""
    try:
        if YahooDownload is None:
            return {"success": False, "result": None, "error": "Class YahooDownload is not available, path may need adjustment"}
        
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
        
        instance = YahooDownload(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="iqfeedtool", description="IQFeedTool class")
def iqfeedtool(*args, **kwargs):
    """IQFeedTool class"""
    try:
        if IQFeedTool is None:
            return {"success": False, "result": None, "error": "Class IQFeedTool is not available, path may need adjustment"}
        
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
        
        instance = IQFeedTool(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="influxdbtool", description="InfluxDBTool class")
def influxdbtool(*args, **kwargs):
    """InfluxDBTool class"""
    try:
        if InfluxDBTool is None:
            return {"success": False, "result": None, "error": "Class InfluxDBTool is not available, path may need adjustment"}
        
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
        
        instance = InfluxDBTool(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_args", description="Auto-wrapped function parse_args")
def parse_args(payload: dict):
    try:
        if parse_args is None:
            return {"success": False, "result": None, "error": "Function parse_args is not available"}
        result = parse_args(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="runstrategy", description="Auto-wrapped function runstrategy")
def runstrategy(payload: dict):
    try:
        if runstrategy is None:
            return {"success": False, "result": None, "error": "Function runstrategy is not available"}
        result = runstrategy(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="pairtradingstrategy", description="PairTradingStrategy class")
def pairtradingstrategy(*args, **kwargs):
    """PairTradingStrategy class"""
    try:
        if PairTradingStrategy is None:
            return {"success": False, "result": None, "error": "Class PairTradingStrategy is not available, path may need adjustment"}
        
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
        
        instance = PairTradingStrategy(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="weekdaysfiller", description="WeekDaysFiller class")
def weekdaysfiller(*args, **kwargs):
    """WeekDaysFiller class"""
    try:
        if WeekDaysFiller is None:
            return {"success": False, "result": None, "error": "Class WeekDaysFiller is not available, path may need adjustment"}
        
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
        
        instance = WeekDaysFiller(*converted_args, **converted_kwargs)
        return {"success": True, "result": str(instance), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="parse_args", description="Auto-wrapped function parse_args")
def parse_args(payload: dict):
    try:
        if parse_args is None:
            return {"success": False, "result": None, "error": "Function parse_args is not available"}
        result = parse_args(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}

@mcp.tool(name="runstrat", description="Auto-wrapped function runstrat")
def runstrat(payload: dict):
    try:
        if runstrat is None:
            return {"success": False, "result": None, "error": "Function runstrat is not available"}
        result = runstrat(**payload)
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}



def create_app():
    """Create and return FastMCP application instance"""
    return mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)