import os
import sys
from typing import Optional, List, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from obspy import read, read_events, read_inventory, UTCDateTime
from obspy.clients.fdsn import Client as FDSNClient
from obspy.geodetics import gps2dist_azimuth
from obspy.taup import TauPyModel

mcp = FastMCP("obspy_mcp_service")


@mcp.tool(name="read_waveforms", description="Read waveform files into ObsPy Stream and summarize traces.")
def read_waveforms(path: str, format: Optional[str] = None) -> Dict[str, Any]:
    """
    Read waveform data from a file path and return a concise summary.

    Parameters:
    - path: Path to waveform file.
    - format: Optional ObsPy format hint (e.g., MSEED, SAC).

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        st = read(path, format=format) if format else read(path)
        result = {
            "trace_count": len(st),
            "traces": [
                {
                    "id": tr.id,
                    "starttime": str(tr.stats.starttime),
                    "endtime": str(tr.stats.endtime),
                    "sampling_rate": float(tr.stats.sampling_rate),
                    "npts": int(tr.stats.npts),
                }
                for tr in st
            ],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="read_event_catalog", description="Read seismic event catalog and summarize events.")
def read_event_catalog(path: str, format: Optional[str] = None) -> Dict[str, Any]:
    """
    Read event catalog data and return summary information.

    Parameters:
    - path: Path to event catalog file.
    - format: Optional ObsPy format hint (e.g., QUAKEML).

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        catalog = read_events(path, format=format) if format else read_events(path)
        events = []
        for ev in catalog:
            origin = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
            magnitude = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
            events.append(
                {
                    "resource_id": str(ev.resource_id) if ev.resource_id else None,
                    "time": str(origin.time) if origin and origin.time else None,
                    "latitude": float(origin.latitude) if origin and origin.latitude is not None else None,
                    "longitude": float(origin.longitude) if origin and origin.longitude is not None else None,
                    "depth_m": float(origin.depth) if origin and origin.depth is not None else None,
                    "magnitude": float(magnitude.mag) if magnitude and magnitude.mag is not None else None,
                    "magnitude_type": magnitude.magnitude_type if magnitude else None,
                }
            )
        return {"success": True, "result": {"event_count": len(catalog), "events": events}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="read_station_inventory", description="Read station metadata inventory and summarize networks/stations.")
def read_station_inventory(path: str, format: Optional[str] = None) -> Dict[str, Any]:
    """
    Read station inventory and return hierarchy summary.

    Parameters:
    - path: Path to station metadata file.
    - format: Optional ObsPy format hint (e.g., STATIONXML).

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        inv = read_inventory(path, format=format) if format else read_inventory(path)
        networks = []
        for net in inv:
            networks.append(
                {
                    "code": net.code,
                    "station_count": len(net.stations),
                    "stations": [st.code for st in net.stations],
                }
            )
        return {"success": True, "result": {"network_count": len(inv.networks), "networks": networks}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="fetch_fdsn_events", description="Fetch event metadata from an FDSN service.")
def fetch_fdsn_events(
    base_url: str,
    starttime: str,
    endtime: str,
    minmagnitude: Optional[float] = None,
    maxmagnitude: Optional[float] = None,
    limit: int = 20,
) -> Dict[str, Any]:
    """
    Query an FDSN event service and return summarized events.

    Parameters:
    - base_url: FDSN provider base URL or service key (e.g., IRIS).
    - starttime: ISO date-time string.
    - endtime: ISO date-time string.
    - minmagnitude: Optional minimum magnitude filter.
    - maxmagnitude: Optional maximum magnitude filter.
    - limit: Maximum number of returned events.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        client = FDSNClient(base_url=base_url)
        kwargs: Dict[str, Any] = {
            "starttime": UTCDateTime(starttime),
            "endtime": UTCDateTime(endtime),
            "limit": limit,
        }
        if minmagnitude is not None:
            kwargs["minmagnitude"] = minmagnitude
        if maxmagnitude is not None:
            kwargs["maxmagnitude"] = maxmagnitude

        cat = client.get_events(**kwargs)
        events = []
        for ev in cat:
            origin = ev.preferred_origin() or (ev.origins[0] if ev.origins else None)
            magnitude = ev.preferred_magnitude() or (ev.magnitudes[0] if ev.magnitudes else None)
            events.append(
                {
                    "time": str(origin.time) if origin and origin.time else None,
                    "latitude": float(origin.latitude) if origin and origin.latitude is not None else None,
                    "longitude": float(origin.longitude) if origin and origin.longitude is not None else None,
                    "depth_m": float(origin.depth) if origin and origin.depth is not None else None,
                    "magnitude": float(magnitude.mag) if magnitude and magnitude.mag is not None else None,
                    "magnitude_type": magnitude.magnitude_type if magnitude else None,
                }
            )
        return {"success": True, "result": {"event_count": len(cat), "events": events}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="fetch_fdsn_waveforms", description="Fetch waveform data from an FDSN dataselect endpoint.")
def fetch_fdsn_waveforms(
    base_url: str,
    network: str,
    station: str,
    location: str,
    channel: str,
    starttime: str,
    endtime: str,
) -> Dict[str, Any]:
    """
    Query waveform traces from an FDSN service and return trace summaries.

    Parameters:
    - base_url: FDSN provider base URL or service key.
    - network: Network code.
    - station: Station code.
    - location: Location code (use '' or '--' as needed).
    - channel: Channel code pattern.
    - starttime: ISO date-time string.
    - endtime: ISO date-time string.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        client = FDSNClient(base_url=base_url)
        st = client.get_waveforms(
            network=network,
            station=station,
            location=location,
            channel=channel,
            starttime=UTCDateTime(starttime),
            endtime=UTCDateTime(endtime),
        )
        result = {
            "trace_count": len(st),
            "traces": [
                {
                    "id": tr.id,
                    "starttime": str(tr.stats.starttime),
                    "endtime": str(tr.stats.endtime),
                    "sampling_rate": float(tr.stats.sampling_rate),
                    "npts": int(tr.stats.npts),
                }
                for tr in st
            ],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="compute_geodetic_distance", description="Compute distance and azimuth between two coordinates.")
def compute_geodetic_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> Dict[str, Any]:
    """
    Compute geodetic distance and forward/back azimuth.

    Parameters:
    - lat1: Latitude of point 1.
    - lon1: Longitude of point 1.
    - lat2: Latitude of point 2.
    - lon2: Longitude of point 2.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        distance_m, azimuth_deg, back_azimuth_deg = gps2dist_azimuth(lat1, lon1, lat2, lon2)
        return {
            "success": True,
            "result": {
                "distance_m": float(distance_m),
                "distance_km": float(distance_m) / 1000.0,
                "azimuth_deg": float(azimuth_deg),
                "back_azimuth_deg": float(back_azimuth_deg),
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="compute_travel_times", description="Compute seismic phase travel times using TauP models.")
def compute_travel_times(
    model_name: str,
    source_depth_km: float,
    distance_degree: float,
    phase_list: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Compute travel times for seismic phases.

    Parameters:
    - model_name: TauP velocity model (e.g., iasp91, ak135).
    - source_depth_km: Source depth in km.
    - distance_degree: Epicentral distance in degrees.
    - phase_list: Optional list of phase names to filter.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        model = TauPyModel(model=model_name)
        arrivals = model.get_travel_times(
            source_depth_in_km=source_depth_km,
            distance_in_degree=distance_degree,
            phase_list=phase_list if phase_list else None,
        )
        result = [
            {
                "phase": arr.name,
                "time_s": float(arr.time),
                "ray_param_s_deg": float(arr.ray_param_sec_degree),
                "takeoff_angle_deg": float(arr.takeoff_angle),
                "incident_angle_deg": float(arr.incident_angle),
            }
            for arr in arrivals
        ]
        return {"success": True, "result": {"arrival_count": len(result), "arrivals": result}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()