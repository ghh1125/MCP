import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

import dedupe
from dedupe import canonical as canonical_mod
from dedupe import convenience as convenience_mod
from dedupe import core as core_mod
from dedupe import lev_enshtein as _invalid  # noqa: F401
from dedupe import serializer as serializer_mod

mcp = FastMCP("dedupe_service")


@mcp.tool(
    name="dedupe_version",
    description="Get the installed dedupe package version.",
)
def dedupe_version() -> dict[str, Any]:
    """
    Returns the dedupe package version.

    Returns:
        A dictionary with:
        - success: bool indicating whether retrieval was successful
        - result: version string on success
        - error: error message on failure
    """
    try:
        version = getattr(dedupe, "__version__", "unknown")
        return {"success": True, "result": version, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="canonicalize_record_cluster",
    description="Generate a canonical representation for a cluster of records.",
)
def canonicalize_record_cluster(records: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Build a canonical record from a list of record dictionaries.

    Parameters:
        records: List of record dictionaries representing one entity cluster.

    Returns:
        A dictionary with:
        - success: bool indicating whether canonicalization succeeded
        - result: canonical record dictionary on success
        - error: error message on failure
    """
    try:
        result = canonical_mod.getCanonicalRep(records)
        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="peek_csv_header",
    description="Inspect CSV file headers and sample rows using dedupe convenience utilities.",
)
def peek_csv_header(file_path: str, sample_size: int = 5) -> dict[str, Any]:
    """
    Read CSV header and a small sample of rows.

    Parameters:
        file_path: Path to CSV file.
        sample_size: Number of data rows to sample after the header.

    Returns:
        A dictionary with:
        - success: bool indicating whether operation succeeded
        - result: dict with 'fieldnames' and 'rows'
        - error: error message on failure
    """
    try:
        import csv

        rows: list[dict[str, Any]] = []
        with open(file_path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            for idx, row in enumerate(reader):
                if idx >= sample_size:
                    break
                rows.append(dict(row))
        return {"success": True, "result": {"fieldnames": fieldnames, "rows": rows}, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="freeze_training_settings",
    description="Serialize dedupe settings object to bytes using serializer module.",
)
def freeze_training_settings(settings_obj: Any) -> dict[str, Any]:
    """
    Serialize a dedupe settings-like object.

    Parameters:
        settings_obj: Object that serializer can pickle/dump.

    Returns:
        A dictionary with:
        - success: bool indicating whether serialization succeeded
        - result: serialized byte size on success
        - error: error message on failure
    """
    try:
        import io

        buffer = io.BytesIO()
        serializer_mod.writeTraining(buffer, settings_obj)
        size = len(buffer.getvalue())
        return {"success": True, "result": size, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="score_record_pairs",
    description="Score precomputed feature vectors for candidate record pairs.",
)
def score_record_pairs(
    features: list[list[float]],
    weights: list[float],
    bias: float = 0.0,
) -> dict[str, Any]:
    """
    Score record-pair feature vectors via dedupe.core logistic scoring helper.

    Parameters:
        features: 2D list where each inner list is a feature vector.
        weights: Model weight vector with same length as each feature vector.
        bias: Optional intercept term.

    Returns:
        A dictionary with:
        - success: bool indicating whether scoring succeeded
        - result: list of probabilities/scores
        - error: error message on failure
    """
    try:
        import numpy as np

        X = np.asarray(features, dtype="float64")
        w = np.asarray(weights, dtype="float64")
        if X.ndim != 2:
            raise ValueError("features must be a 2D list")
        if w.ndim != 1:
            raise ValueError("weights must be a 1D list")
        if X.shape[1] != w.shape[0]:
            raise ValueError("weights length must match feature vector length")

        scores = core_mod.scoreDuplicates(X, w, bias)
        return {"success": True, "result": scores.tolist(), "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="match_score_summary",
    description="Create a quick summary over pair match scores.",
)
def match_score_summary(scores: list[float], threshold: float = 0.5) -> dict[str, Any]:
    """
    Summarize match scores.

    Parameters:
        scores: List of match probabilities/scores.
        threshold: Threshold used to count likely matches.

    Returns:
        A dictionary with:
        - success: bool indicating whether summary succeeded
        - result: summary dictionary
        - error: error message on failure
    """
    try:
        if not scores:
            summary = {"count": 0, "min": None, "max": None, "mean": None, "above_threshold": 0}
            return {"success": True, "result": summary, "error": None}

        count = len(scores)
        min_v = min(scores)
        max_v = max(scores)
        mean_v = sum(scores) / count
        above = sum(1 for s in scores if s >= threshold)
        summary = {
            "count": count,
            "min": min_v,
            "max": max_v,
            "mean": mean_v,
            "above_threshold": above,
        }
        return {"success": True, "result": summary, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()