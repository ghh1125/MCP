import os
import sys
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("aizynthfinder_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _fail(error: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(error)}


@mcp.tool(
    name="run_aizynthcli",
    description="Run aizynthfinder CLI-like retrosynthesis workflow for target SMILES.",
)
def run_aizynthcli(
    config_path: str,
    smiles: str,
    output_file: Optional[str] = None,
    nproc: int = 1,
) -> Dict[str, Any]:
    """
    Execute retrosynthesis search using AiZynthFinder high-level API.

    Parameters:
    - config_path: Path to AiZynthFinder YAML configuration file.
    - smiles: Target molecule SMILES.
    - output_file: Optional output JSON path.
    - nproc: Number of processes/threads where supported.

    Returns:
    - Dictionary with success/result/error fields.
    """
    try:
        from aizynthfinder.aizynthfinder import AiZynthFinder

        finder = AiZynthFinder(configfile=config_path)
        finder.target_smiles = smiles
        finder.prepare_tree()
        finder.tree_search()
        finder.build_routes()

        routes_dict = finder.routes.dict_with_extra(include_scores=True)

        if output_file:
            import json

            with open(output_file, "w", encoding="utf-8") as fobj:
                json.dump(routes_dict, fobj, indent=2)

        return _ok(
            {
                "target_smiles": smiles,
                "num_routes": len(finder.routes),
                "routes": routes_dict,
                "nproc": nproc,
                "output_file": output_file,
            }
        )
    except Exception as exc:
        return _fail(exc)


@mcp.tool(
    name="analyze_routes",
    description="Analyze retrosynthesis routes from a route dictionary or JSON file.",
)
def analyze_routes(
    routes_json_path: Optional[str] = None,
    route_dictionary: Optional[dict] = None,
) -> Dict[str, Any]:
    """
    Analyze route content and return summary metrics.

    Parameters:
    - routes_json_path: Path to routes JSON produced by AiZynthFinder.
    - route_dictionary: In-memory route dictionary.

    Returns:
    - Dictionary with success/result/error fields.
    """
    try:
        import json

        routes_data = route_dictionary
        if routes_data is None:
            if not routes_json_path:
                raise ValueError("Provide either routes_json_path or route_dictionary")
            with open(routes_json_path, "r", encoding="utf-8") as fobj:
                routes_data = json.load(fobj)

        routes = routes_data.get("routes", []) if isinstance(routes_data, dict) else []
        summary = {
            "num_routes": len(routes),
            "has_data": len(routes) > 0,
            "scores": [route.get("score") for route in routes if isinstance(route, dict)],
        }
        return _ok(summary)
    except Exception as exc:
        return _fail(exc)


@mcp.tool(
    name="download_public_data",
    description="Download public data assets used by aizynthfinder.",
)
def download_public_data(destination: str) -> Dict[str, Any]:
    """
    Download public models/data via project utility.

    Parameters:
    - destination: Local destination directory.

    Returns:
    - Dictionary with success/result/error fields.
    """
    try:
        from aizynthfinder.tools.download_public_data import main as download_main

        os.makedirs(destination, exist_ok=True)
        cwd = os.getcwd()
        try:
            os.chdir(destination)
            download_main()
        finally:
            os.chdir(cwd)

        return _ok({"destination": destination})
    except Exception as exc:
        return _fail(exc)


@mcp.tool(
    name="make_stock",
    description="Create stock file/database from input molecule file(s).",
)
def make_stock(
    input_files: List[str],
    output_path: str,
    source_type: str = "plain",
) -> Dict[str, Any]:
    """
    Build stock artifacts from molecular sources.

    Parameters:
    - input_files: List of input files.
    - output_path: Output stock path.
    - source_type: Input source type (tool-dependent).

    Returns:
    - Dictionary with success/result/error fields.
    """
    try:
        from aizynthfinder.tools.make_stock import make_stock as make_stock_func

        make_stock_func(input_files=input_files, output=output_path, source=source_type)
        return _ok({"output_path": output_path, "input_files": input_files, "source_type": source_type})
    except Exception as exc:
        return _fail(exc)


@mcp.tool(
    name="cat_output",
    description="Read and concatenate/inspect aizynthfinder output artifacts.",
)
def cat_output(paths: List[str]) -> Dict[str, Any]:
    """
    Concatenate output files and return combined text.

    Parameters:
    - paths: List of file paths to inspect.

    Returns:
    - Dictionary with success/result/error fields.
    """
    try:
        combined_parts: List[str] = []
        for path in paths:
            with open(path, "r", encoding="utf-8") as fobj:
                combined_parts.append(fobj.read())
        return _ok({"content": "\n".join(combined_parts), "files": paths})
    except Exception as exc:
        return _fail(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()