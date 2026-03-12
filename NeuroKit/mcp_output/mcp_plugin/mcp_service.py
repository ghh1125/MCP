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
import neurokit2 as nk
import numpy as np
import pandas as pd

mcp = FastMCP("neurokit2_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


def _to_array(signal: List[float]) -> np.ndarray:
    return np.asarray(signal, dtype=float)


def _df_to_records(df: pd.DataFrame, limit: int = 2000) -> List[Dict[str, Any]]:
    if len(df) > limit:
        df = df.head(limit)
    return df.replace({np.nan: None}).to_dict(orient="records")


@mcp.tool(name="nk_ecg_simulate", description="Simulate an ECG signal.")
def nk_ecg_simulate(duration: float = 10.0, sampling_rate: int = 250, heart_rate: int = 70) -> Dict[str, Any]:
    """
    Simulate an ECG waveform.

    Parameters:
        duration: Signal duration in seconds.
        sampling_rate: Sampling frequency in Hz.
        heart_rate: Target heart rate in beats per minute.

    Returns:
        Dict with success/result/error where result is a list of ECG values.
    """
    try:
        signal = nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate, heart_rate=heart_rate)
        return _ok(signal.tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_ecg_process", description="Process ECG signal and extract standard features.")
def nk_ecg_process(signal: List[float], sampling_rate: int = 250) -> Dict[str, Any]:
    """
    Process ECG signal into cleaned signal and event markers.

    Parameters:
        signal: Raw ECG signal values.
        sampling_rate: Sampling frequency in Hz.

    Returns:
        Dict with success/result/error where result includes processed records and info.
    """
    try:
        df, info = nk.ecg_process(_to_array(signal), sampling_rate=sampling_rate)
        result = {"data": _df_to_records(df), "info": info}
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_hrv_time", description="Compute time-domain HRV metrics from R-peaks.")
def nk_hrv_time(peaks: List[int], sampling_rate: int = 250) -> Dict[str, Any]:
    """
    Compute time-domain HRV metrics.

    Parameters:
        peaks: R-peak sample indices.
        sampling_rate: Sampling frequency in Hz.

    Returns:
        Dict with success/result/error where result is HRV metrics record.
    """
    try:
        peak_dict = {"ECG_R_Peaks": np.asarray(peaks, dtype=int)}
        out = nk.hrv_time(peak_dict, sampling_rate=sampling_rate)
        return _ok(_df_to_records(out, limit=10))
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_eda_process", description="Process EDA signal into phasic/tonic components and peaks.")
def nk_eda_process(signal: List[float], sampling_rate: int = 250) -> Dict[str, Any]:
    """
    Process EDA signal.

    Parameters:
        signal: Raw EDA signal values.
        sampling_rate: Sampling frequency in Hz.

    Returns:
        Dict with success/result/error where result includes data records and info.
    """
    try:
        df, info = nk.eda_process(_to_array(signal), sampling_rate=sampling_rate)
        return _ok({"data": _df_to_records(df), "info": info})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_rsp_process", description="Process respiration signal and derive respiratory features.")
def nk_rsp_process(signal: List[float], sampling_rate: int = 1000) -> Dict[str, Any]:
    """
    Process respiration (RSP) signal.

    Parameters:
        signal: Raw respiration signal values.
        sampling_rate: Sampling frequency in Hz.

    Returns:
        Dict with success/result/error where result includes data records and info.
    """
    try:
        df, info = nk.rsp_process(_to_array(signal), sampling_rate=sampling_rate)
        return _ok({"data": _df_to_records(df), "info": info})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_ppg_process", description="Process PPG signal and extract peaks/rate.")
def nk_ppg_process(signal: List[float], sampling_rate: int = 100) -> Dict[str, Any]:
    """
    Process PPG signal.

    Parameters:
        signal: Raw PPG signal values.
        sampling_rate: Sampling frequency in Hz.

    Returns:
        Dict with success/result/error where result includes data records and info.
    """
    try:
        df, info = nk.ppg_process(_to_array(signal), sampling_rate=sampling_rate)
        return _ok({"data": _df_to_records(df), "info": info})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_signal_filter", description="Apply NeuroKit filtering to a signal.")
def nk_signal_filter(
    signal: List[float],
    sampling_rate: int = 1000,
    lowcut: Optional[float] = None,
    highcut: Optional[float] = None,
    method: str = "butterworth",
    order: int = 2,
) -> Dict[str, Any]:
    """
    Filter a signal with configurable cutoffs and filter method.

    Parameters:
        signal: Input signal values.
        sampling_rate: Sampling frequency in Hz.
        lowcut: Low cutoff frequency in Hz.
        highcut: High cutoff frequency in Hz.
        method: Filter method name supported by NeuroKit.
        order: Filter order.

    Returns:
        Dict with success/result/error where result is filtered signal values.
    """
    try:
        filtered = nk.signal_filter(
            _to_array(signal),
            sampling_rate=sampling_rate,
            lowcut=lowcut,
            highcut=highcut,
            method=method,
            order=order,
        )
        return _ok(np.asarray(filtered).tolist())
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_signal_psd", description="Compute power spectral density of a signal.")
def nk_signal_psd(
    signal: List[float],
    sampling_rate: int = 1000,
    method: str = "welch",
    min_frequency: float = 0.0,
    max_frequency: Optional[float] = None,
    normalize: bool = True,
) -> Dict[str, Any]:
    """
    Compute signal PSD.

    Parameters:
        signal: Input signal values.
        sampling_rate: Sampling frequency in Hz.
        method: PSD method.
        min_frequency: Minimum frequency in Hz.
        max_frequency: Maximum frequency in Hz.
        normalize: Whether to normalize PSD.

    Returns:
        Dict with success/result/error where result is PSD records.
    """
    try:
        psd = nk.signal_psd(
            _to_array(signal),
            sampling_rate=sampling_rate,
            method=method,
            min_frequency=min_frequency,
            max_frequency=max_frequency,
            normalize=normalize,
        )
        return _ok(_df_to_records(psd, limit=5000))
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_complexity", description="Compute complexity features for a time series.")
def nk_complexity(signal: List[float], which: str = "makowski2022", delay: int = 1, dimension: int = 2) -> Dict[str, Any]:
    """
    Compute a standard set of complexity metrics.

    Parameters:
        signal: Input signal values.
        which: Complexity preset.
        delay: Embedding delay.
        dimension: Embedding dimension.

    Returns:
        Dict with success/result/error where result includes metrics and info.
    """
    try:
        metrics, info = nk.complexity(_to_array(signal), which=which, delay=delay, dimension=dimension)
        if isinstance(metrics, pd.DataFrame):
            metric_result: Any = _df_to_records(metrics, limit=10)
        elif isinstance(metrics, pd.Series):
            metric_result = metrics.to_dict()
        else:
            metric_result = metrics
        return _ok({"metrics": metric_result, "info": info})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="nk_events_find", description="Find events in a digital/event channel.")
def nk_events_find(event_channel: List[float], threshold: str = "auto", duration_min: int = 1) -> Dict[str, Any]:
    """
    Detect events from an event channel.

    Parameters:
        event_channel: Event channel values.
        threshold: Threshold strategy or numeric-like string.
        duration_min: Minimum event duration in samples.

    Returns:
        Dict with success/result/error where result contains event indices and metadata.
    """
    try:
        events = nk.events_find(_to_array(event_channel), threshold=threshold, duration_min=duration_min)
        serializable = {k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in events.items()}
        return _ok(serializable)
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()