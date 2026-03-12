import os
import sys
from typing import Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from psychopy.plugins import activatePlugins, listPlugins, loadPlugin
from psychopy.session import Session

mcp = FastMCP("psychopy_core_service")


@mcp.tool(
    name="plugins_list",
    description="List available PsychoPy plugins discovered by the plugin system.",
)
def plugins_list(which: str = "all") -> dict:
    """
    List PsychoPy plugins.

    Parameters:
    - which: Plugin subset selector (typically "all", "loaded", etc. depending on PsychoPy version).

    Returns:
    - dict with success/result/error.
    """
    try:
        result = listPlugins(which=which)
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="plugins_activate",
    description="Activate plugins by name, optionally suppressing startup warnings.",
)
def plugins_activate(plugin: str, suppress_warnings: bool = True) -> dict:
    """
    Activate one or more PsychoPy plugins.

    Parameters:
    - plugin: Plugin name or comma-separated plugin names.
    - suppress_warnings: Whether to suppress activation warnings where supported.

    Returns:
    - dict with success/result/error.
    """
    try:
        plugin_names: List[str] = [p.strip() for p in plugin.split(",") if p.strip()]
        if not plugin_names:
            return {"success": False, "result": None, "error": "No plugin name provided"}
        result = activatePlugins(which=plugin_names, suppressWarnings=suppress_warnings)
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="plugin_load",
    description="Load a specific PsychoPy plugin immediately.",
)
def plugin_load(plugin: str) -> dict:
    """
    Load a specific plugin.

    Parameters:
    - plugin: Exact plugin name.

    Returns:
    - dict with success/result/error.
    """
    try:
        result = loadPlugin(plugin)
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="session_create",
    description="Create a PsychoPy Session with explicit participant and session identifiers.",
)
def session_create(participant: str, session: str, experiment_path: Optional[str] = None) -> dict:
    """
    Create a PsychoPy Session object.

    Parameters:
    - participant: Participant identifier.
    - session: Session identifier.
    - experiment_path: Optional experiment file/path context.

    Returns:
    - dict with success/result/error.
    """
    try:
        kwargs = {"participant": participant, "session": session}
        if experiment_path:
            kwargs["experimentPath"] = experiment_path
        sess = Session(**kwargs)
        result = {
            "participant": getattr(sess, "participant", participant),
            "session": getattr(sess, "session", session),
            "experimentPath": getattr(sess, "experimentPath", experiment_path),
            "class": sess.__class__.__name__,
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp