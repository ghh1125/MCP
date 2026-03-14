import os
import sys
from typing import Optional, Dict, Any, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("mne_python_service")


def _safe_import_mne():
    try:
        import mne  # type: ignore
        return True, mne, None
    except Exception as exc:
        return False, None, str(exc)


@mcp.tool(name="mne_get_version", description="Get installed MNE version information.")
def mne_get_version() -> Dict[str, Any]:
    """
    Return MNE package version.

    Returns:
        Dict with:
        - success: bool indicating operation status
        - result: version string when successful
        - error: error string when failed
    """
    ok, mne_mod, err = _safe_import_mne()
    if not ok:
        return {"success": False, "result": None, "error": err}
    try:
        version = getattr(mne_mod, "__version__", "unknown")
        return {"success": True, "result": version, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="mne_get_config", description="Read MNE configuration value by key.")
def mne_get_config(key: str, default: Optional[str] = None) -> Dict[str, Any]:
    """
    Read a single MNE config key.

    Parameters:
        key: Configuration key to lookup.
        default: Optional fallback if key is not found.

    Returns:
        Dict with:
        - success: bool
        - result: config value
        - error: error message when failed
    """
    ok, mne_mod, err = _safe_import_mne()
    if not ok:
        return {"success": False, "result": None, "error": err}
    try:
        value = mne_mod.get_config(key=key, default=default)
        return {"success": True, "result": value, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="mne_set_config", description="Set an MNE configuration key to a value.")
def mne_set_config(key: str, value: str, set_env: bool = False) -> Dict[str, Any]:
    """
    Set a single MNE config key.

    Parameters:
        key: Configuration key.
        value: Configuration value.
        set_env: If True, also set environment variable for current process.

    Returns:
        Dict with:
        - success: bool
        - result: True when set successfully
        - error: error message when failed
    """
    ok, mne_mod, err = _safe_import_mne()
    if not ok:
        return {"success": False, "result": None, "error": err}
    try:
        mne_mod.set_config(key=key, value=value, set_env=set_env)
        return {"success": True, "result": True, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="mne_create_info", description="Create an MNE Info object from channels and sampling frequency.")
def mne_create_info(ch_names: List[str], sfreq: float, ch_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create a lightweight channel metadata structure.

    Parameters:
        ch_names: List of channel names.
        sfreq: Sampling frequency in Hz.
        ch_types: Optional list of channel types aligned with ch_names.

    Returns:
        Dict with:
        - success: bool
        - result: serializable summary of created Info
        - error: error message when failed
    """
    ok, mne_mod, err = _safe_import_mne()
    if not ok:
        return {"success": False, "result": None, "error": err}
    try:
        info = mne_mod.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
        result = {
            "nchan": int(info["nchan"]),
            "sfreq": float(info["sfreq"]),
            "ch_names": list(info["ch_names"]),
            "highpass": float(info.get("highpass", 0.0) or 0.0),
            "lowpass": float(info.get("lowpass", 0.0) or 0.0),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="mne_compute_events", description="Detect events from a stim channel in a raw FIF file.")
def mne_compute_events(
    raw_fif_path: str,
    stim_channel: Optional[str] = None,
    shortest_event: int = 1,
    min_duration: float = 0.0,
) -> Dict[str, Any]:
    """
    Load raw FIF and compute events from stimulation channel.

    Parameters:
        raw_fif_path: Path to a readable raw FIF file.
        stim_channel: Optional stim channel name. If None, MNE default detection is used.
        shortest_event: Minimum number of samples for an event.
        min_duration: Minimum event duration in seconds.

    Returns:
        Dict with:
        - success: bool
        - result: event count and preview rows
        - error: error message when failed
    """
    ok, mne_mod, err = _safe_import_mne()
    if not ok:
        return {"success": False, "result": None, "error": err}
    try:
        raw = mne_mod.io.read_raw_fif(raw_fif_path, preload=False, verbose=False)
        events = mne_mod.find_events(
            raw,
            stim_channel=stim_channel,
            shortest_event=shortest_event,
            min_duration=min_duration,
            verbose=False,
        )
        preview = events[:20].tolist() if len(events) > 0 else []
        return {
            "success": True,
            "result": {"count": int(len(events)), "preview": preview},
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="mne_estimate_rank", description="Estimate data rank from an epochs or raw FIF file.")
def mne_estimate_rank(fif_path: str, tol: Optional[float] = None) -> Dict[str, Any]:
    """
    Estimate numerical rank from MNE data object loaded from FIF.

    Parameters:
        fif_path: Path to raw or epochs FIF file.
        tol: Optional tolerance passed to rank estimator.

    Returns:
        Dict with:
        - success: bool
        - result: estimated rank dictionary or scalar
        - error: error message when failed
    """
    ok, mne_mod, err = _safe_import_mne()
    if not ok:
        return {"success": False, "result": None, "error": err}
    try:
        result_obj: Any
        try:
            raw = mne_mod.io.read_raw_fif(fif_path, preload=False, verbose=False)
            result_obj = mne_mod.compute_rank(raw, tol=tol, verbose=False)
        except Exception:
            epochs = mne_mod.read_epochs(fif_path, preload=False, verbose=False)
            result_obj = mne_mod.compute_rank(epochs, tol=tol, verbose=False)

        if isinstance(result_obj, dict):
            serializable = {str(k): int(v) for k, v in result_obj.items()}
        else:
            serializable = int(result_obj)
        return {"success": True, "result": serializable, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()