import os
import sys
from datetime import datetime, date
from typing import List, Optional, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from dateutil import easter
from dateutil.parser import parse as dt_parse
from dateutil.parser import isoparse
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, rrulestr, YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY
from dateutil.tz import gettz, UTC


mcp = FastMCP("dateutil_service")


_FREQ_MAP = {
    "YEARLY": YEARLY,
    "MONTHLY": MONTHLY,
    "WEEKLY": WEEKLY,
    "DAILY": DAILY,
    "HOURLY": HOURLY,
    "MINUTELY": MINUTELY,
    "SECONDLY": SECONDLY,
}


def _safe_result(value: Any) -> Dict[str, Any]:
    return {"success": True, "result": value, "error": None}


def _safe_error(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="parse_datetime", description="Parse a general datetime string into ISO format.")
def parse_datetime(
    text: str,
    dayfirst: bool = False,
    yearfirst: bool = False,
    default_iso: Optional[str] = None
) -> Dict[str, Any]:
    """
    Parse a datetime string using dateutil.parser.parse.

    Parameters:
    - text: Input datetime text to parse.
    - dayfirst: Whether to interpret ambiguous dates as day-first.
    - yearfirst: Whether to interpret ambiguous dates as year-first.
    - default_iso: Optional ISO datetime used as default values for missing parts.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        default_dt = None
        if default_iso:
            default_dt = datetime.fromisoformat(default_iso)
        parsed = dt_parse(text, dayfirst=dayfirst, yearfirst=yearfirst, default=default_dt)
        return _safe_result(parsed.isoformat())
    except Exception as exc:
        return _safe_error(exc)


@mcp.tool(name="parse_iso_datetime", description="Parse an ISO-8601 datetime string.")
def parse_iso_datetime(text: str) -> Dict[str, Any]:
    """
    Parse an ISO-8601 datetime string using dateutil.parser.isoparse.

    Parameters:
    - text: ISO datetime text.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        parsed = isoparse(text)
        return _safe_result(parsed.isoformat())
    except Exception as exc:
        return _safe_error(exc)


@mcp.tool(name="compute_easter", description="Compute Easter date for a given year.")
def compute_easter(year: int, method: int = 3) -> Dict[str, Any]:
    """
    Compute Easter date using dateutil.easter.easter.

    Parameters:
    - year: Target year.
    - method: Easter algorithm (1=Julian, 2=Orthodox, 3=Western).

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        easter_date = easter.easter(year, method=method)
        return _safe_result(easter_date.isoformat())
    except Exception as exc:
        return _safe_error(exc)


@mcp.tool(name="add_relativedelta", description="Apply relative date/time offsets to a datetime.")
def add_relativedelta(
    base_iso: str,
    years: int = 0,
    months: int = 0,
    weeks: int = 0,
    days: int = 0,
    hours: int = 0,
    minutes: int = 0,
    seconds: int = 0
) -> Dict[str, Any]:
    """
    Apply relativedelta offsets to a base datetime.

    Parameters:
    - base_iso: Base datetime in ISO format.
    - years, months, weeks, days, hours, minutes, seconds: Relative offsets.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        base_dt = datetime.fromisoformat(base_iso)
        delta = relativedelta(
            years=years,
            months=months,
            weeks=weeks,
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds,
        )
        out = base_dt + delta
        return _safe_result(out.isoformat())
    except Exception as exc:
        return _safe_error(exc)


@mcp.tool(name="generate_rrule", description="Generate recurrence instances from rrule parameters.")
def generate_rrule(
    dtstart_iso: str,
    freq: str,
    count: int = 10,
    interval: int = 1
) -> Dict[str, Any]:
    """
    Generate recurrence datetimes using dateutil.rrule.rrule.

    Parameters:
    - dtstart_iso: Start datetime in ISO format.
    - freq: Frequency name: YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY, SECONDLY.
    - count: Number of occurrences to produce.
    - interval: Frequency interval.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        freq_key = freq.upper().strip()
        if freq_key not in _FREQ_MAP:
            raise ValueError("Invalid freq value.")
        dtstart = datetime.fromisoformat(dtstart_iso)
        rule = rrule(_FREQ_MAP[freq_key], dtstart=dtstart, count=count, interval=interval)
        items = [item.isoformat() for item in rule]
        return _safe_result(items)
    except Exception as exc:
        return _safe_error(exc)


@mcp.tool(name="expand_rrule_string", description="Expand an iCalendar RRULE string into occurrences.")
def expand_rrule_string(
    rule_text: str,
    dtstart_iso: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    Expand occurrences from an RRULE string using dateutil.rrule.rrulestr.

    Parameters:
    - rule_text: RRULE text (e.g., 'FREQ=DAILY;COUNT=5').
    - dtstart_iso: Optional ISO datetime start.
    - limit: Maximum number of occurrences returned.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        dtstart = datetime.fromisoformat(dtstart_iso) if dtstart_iso else None
        rule = rrulestr(rule_text, dtstart=dtstart)
        items: List[str] = []
        for i, item in enumerate(rule):
            if i >= limit:
                break
            items.append(item.isoformat())
        return _safe_result(items)
    except Exception as exc:
        return _safe_error(exc)


@mcp.tool(name="convert_timezone", description="Convert datetime from one timezone to another.")
def convert_timezone(
    dt_iso: str,
    from_tz_name: str,
    to_tz_name: str
) -> Dict[str, Any]:
    """
    Convert datetime between timezones using dateutil.tz.gettz.

    Parameters:
    - dt_iso: Input datetime in ISO format.
    - from_tz_name: Source timezone name (e.g., 'UTC', 'America/New_York').
    - to_tz_name: Target timezone name.

    Returns:
    - Dictionary with success/result/error.
    """
    try:
        dt = datetime.fromisoformat(dt_iso)
        from_tz = UTC if from_tz_name.upper() == "UTC" else gettz(from_tz_name)
        to_tz = UTC if to_tz_name.upper() == "UTC" else gettz(to_tz_name)
        if from_tz is None or to_tz is None:
            raise ValueError("Invalid timezone name.")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=from_tz)
        else:
            dt = dt.astimezone(from_tz)
        converted = dt.astimezone(to_tz)
        return _safe_result(converted.isoformat())
    except Exception as exc:
        return _safe_error(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()