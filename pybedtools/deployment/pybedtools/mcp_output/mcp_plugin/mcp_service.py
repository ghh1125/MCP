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
import pybedtools
from pybedtools import BedTool

mcp = FastMCP("pybedtools_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(
    name="bedtool_from_string",
    description="Create a BedTool object from a BED/GFF/VCF formatted string and return saved temp path.",
)
def bedtool_from_string(data: str) -> Dict[str, Any]:
    """
    Create a BedTool from in-memory text.

    Parameters:
        data: Interval text content (e.g., BED lines).

    Returns:
        Dict with success/result/error. Result contains temporary file path and feature count.
    """
    try:
        bt = BedTool(data, from_string=True)
        return _ok({"path": bt.fn, "count": len(bt)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_intersect",
    description="Intersect two interval files using pybedtools and return output path and count.",
)
def bedtool_intersect(
    a_path: str,
    b_path: str,
    wa: bool = False,
    wb: bool = False,
    u: bool = False,
    loj: bool = False,
) -> Dict[str, Any]:
    """
    Intersect interval datasets.

    Parameters:
        a_path: Path to first interval file.
        b_path: Path to second interval file.
        wa: Write original A entry for each overlap.
        wb: Write original B entry for each overlap.
        u: Write unique A entries that overlap B.
        loj: Perform left outer join.

    Returns:
        Dict with success/result/error. Result includes output path and number of records.
    """
    try:
        a = BedTool(a_path)
        b = BedTool(b_path)
        out = a.intersect(b, wa=wa, wb=wb, u=u, loj=loj)
        return _ok({"path": out.fn, "count": len(out)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_merge",
    description="Merge overlapping/nearby intervals from a single interval file.",
)
def bedtool_merge(
    input_path: str,
    distance: int = 0,
) -> Dict[str, Any]:
    """
    Merge intervals.

    Parameters:
        input_path: Path to interval file.
        distance: Maximum distance between features to merge.

    Returns:
        Dict with success/result/error. Result includes output path and merged feature count.
    """
    try:
        bt = BedTool(input_path)
        out = bt.merge(d=distance)
        return _ok({"path": out.fn, "count": len(out)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_sort",
    description="Sort intervals and return sorted output path.",
)
def bedtool_sort(input_path: str) -> Dict[str, Any]:
    """
    Sort interval records.

    Parameters:
        input_path: Path to interval file.

    Returns:
        Dict with success/result/error. Result includes sorted path and count.
    """
    try:
        bt = BedTool(input_path)
        out = bt.sort()
        return _ok({"path": out.fn, "count": len(out)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_genome_coverage",
    description="Compute genome coverage statistics for intervals.",
)
def bedtool_genome_coverage(
    input_path: str,
    genome_file: Optional[str] = None,
    strand: Optional[str] = None,
    bg: bool = False,
) -> Dict[str, Any]:
    """
    Run genome coverage.

    Parameters:
        input_path: Path to interval file.
        genome_file: Path to genome file with chrom sizes.
        strand: Optional strand filter ('+' or '-').
        bg: If True, report bedGraph output.

    Returns:
        Dict with success/result/error. Result includes output path and line count.
    """
    try:
        bt = BedTool(input_path)
        kwargs: Dict[str, Any] = {"bg": bg}
        if genome_file:
            kwargs["g"] = genome_file
        if strand:
            kwargs["strand"] = strand
        out = bt.genome_coverage(**kwargs)
        return _ok({"path": out.fn, "count": len(out)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_closest",
    description="Find closest features from B for each feature in A.",
)
def bedtool_closest(
    a_path: str,
    b_path: str,
    d: bool = True,
    t: str = "all",
) -> Dict[str, Any]:
    """
    Compute closest intervals.

    Parameters:
        a_path: Path to A intervals.
        b_path: Path to B intervals.
        d: Report distance column.
        t: Tie mode ('all', 'first', or 'last').

    Returns:
        Dict with success/result/error. Result includes output path and count.
    """
    try:
        a = BedTool(a_path)
        b = BedTool(b_path)
        out = a.closest(b, d=d, t=t)
        return _ok({"path": out.fn, "count": len(out)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_slop",
    description="Expand intervals by fixed bp using a genome file.",
)
def bedtool_slop(
    input_path: str,
    genome_file: str,
    left: int = 0,
    right: int = 0,
    both: int = 0,
) -> Dict[str, Any]:
    """
    Expand intervals with slop.

    Parameters:
        input_path: Path to interval file.
        genome_file: Path to chrom sizes file.
        left: Left extension in bp.
        right: Right extension in bp.
        both: Symmetric extension in bp.

    Returns:
        Dict with success/result/error. Result includes output path and count.
    """
    try:
        bt = BedTool(input_path)
        if both > 0:
            out = bt.slop(g=genome_file, b=both)
        else:
            out = bt.slop(g=genome_file, l=left, r=right)
        return _ok({"path": out.fn, "count": len(out)})
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="bedtool_head",
    description="Return first N lines from an interval file for quick inspection.",
)
def bedtool_head(input_path: str, n: int = 10) -> Dict[str, Any]:
    """
    Preview interval content.

    Parameters:
        input_path: Path to interval file.
        n: Number of leading lines to return.

    Returns:
        Dict with success/result/error. Result contains up to n lines.
    """
    try:
        bt = BedTool(input_path)
        lines: List[str] = []
        for i, feature in enumerate(bt):
            if i >= n:
                break
            lines.append(str(feature).rstrip("\n"))
        return _ok(lines)
    except Exception as e:
        return _err(str(e))


@mcp.tool(
    name="pybedtools_version_info",
    description="Return pybedtools and BEDTools version information.",
)
def pybedtools_version_info() -> Dict[str, Any]:
    """
    Get runtime version details.

    Returns:
        Dict with success/result/error. Result includes pybedtools and bedtools versions when available.
    """
    try:
        bedtools_version = None
        try:
            bedtools_version = pybedtools.helpers.get_bedtools_version()
        except Exception:
            bedtools_version = None
        return _ok(
            {
                "pybedtools_version": getattr(pybedtools, "__version__", "unknown"),
                "bedtools_version": bedtools_version,
            }
        )
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()