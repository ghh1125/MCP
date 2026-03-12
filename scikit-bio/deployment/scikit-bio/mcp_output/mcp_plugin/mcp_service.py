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

mcp = FastMCP("scikit_bio_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(exc: Exception) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="package_info", description="Return scikit-bio package metadata and available top-level modules.")
def package_info() -> Dict[str, Any]:
    """
    Get package metadata from scikit-bio.

    Returns:
        A dictionary with success/result/error fields. Result includes version info
        and a list of discovered top-level namespaces.
    """
    try:
        import skbio

        top_level = [
            "alignment",
            "binaries",
            "diversity",
            "embedding",
            "io",
            "metadata",
            "sequence",
            "stats",
            "table",
            "tree",
            "util",
        ]
        result = {
            "package": "skbio",
            "version": getattr(skbio, "__version__", None),
            "top_level_modules": top_level,
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="read_sequence", description="Create a biological sequence object and return basic properties.")
def read_sequence(sequence: str, seq_type: str = "DNA", lowercase: bool = False) -> Dict[str, Any]:
    """
    Build a sequence object (DNA, RNA, Protein, or generic Sequence).

    Args:
        sequence: Raw sequence string.
        seq_type: One of 'DNA', 'RNA', 'Protein', or 'Sequence'.
        lowercase: Whether to lower-case the input before parsing.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        from skbio.sequence import DNA, RNA, Protein, Sequence

        seq_text = sequence.lower() if lowercase else sequence
        type_map = {"DNA": DNA, "RNA": RNA, "Protein": Protein, "Sequence": Sequence}
        if seq_type not in type_map:
            raise ValueError("seq_type must be one of: DNA, RNA, Protein, Sequence")
        cls = type_map[seq_type]
        obj = cls(seq_text)
        result = {
            "type": seq_type,
            "length": len(obj),
            "has_gaps": "-" in str(obj),
            "sequence": str(obj),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="global_pairwise_align_nucleotide", description="Compute global pairwise nucleotide alignment.")
def global_pairwise_align_nucleotide(
    seq1: str,
    seq2: str,
    gap_open_penalty: float = 5.0,
    gap_extend_penalty: float = 2.0,
    match_score: float = 1.0,
    mismatch_score: float = -2.0,
) -> Dict[str, Any]:
    """
    Perform global pairwise nucleotide alignment.

    Args:
        seq1: First nucleotide sequence.
        seq2: Second nucleotide sequence.
        gap_open_penalty: Gap open penalty.
        gap_extend_penalty: Gap extension penalty.
        match_score: Match score.
        mismatch_score: Mismatch score.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        from skbio import DNA
        from skbio.alignment import global_pairwise_align_nucleotide

        aln, score, start_end = global_pairwise_align_nucleotide(
            DNA(seq1),
            DNA(seq2),
            gap_open_penalty=gap_open_penalty,
            gap_extend_penalty=gap_extend_penalty,
            match_score=match_score,
            mismatch_score=mismatch_score,
        )
        result = {
            "score": float(score),
            "start_end_positions": start_end,
            "alignment": str(aln),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="compute_alpha_diversity", description="Compute alpha diversity metric from counts.")
def compute_alpha_diversity(metric: str, counts: List[float]) -> Dict[str, Any]:
    """
    Compute alpha diversity using scikit-bio alpha metrics.

    Args:
        metric: Alpha diversity metric name supported by skbio.diversity.alpha_diversity.
        counts: Feature counts for a single sample.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        import numpy as np
        from skbio.diversity import alpha_diversity

        data = np.asarray([counts], dtype=float)
        vals = alpha_diversity(metric=metric, counts=data, ids=["sample_1"])
        return _ok({"metric": metric, "value": float(vals[0])})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="compute_beta_diversity", description="Compute beta diversity distance matrix from sample counts.")
def compute_beta_diversity(metric: str, counts: List[List[float]], ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Compute beta diversity distance matrix.

    Args:
        metric: Beta diversity metric name (e.g., 'braycurtis', 'jaccard').
        counts: 2D sample-by-feature count matrix.
        ids: Optional sample IDs. If omitted, IDs are auto-generated.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        import numpy as np
        from skbio.diversity import beta_diversity

        arr = np.asarray(counts, dtype=float)
        if arr.ndim != 2:
            raise ValueError("counts must be a 2D matrix")
        if ids is None:
            ids = [f"s{i+1}" for i in range(arr.shape[0])]
        if len(ids) != arr.shape[0]:
            raise ValueError("len(ids) must match number of rows in counts")

        dm = beta_diversity(metric=metric, counts=arr, ids=ids)
        return _ok({"metric": metric, "ids": list(dm.ids), "data": dm.data.tolist()})
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="distance_matrix_stats", description="Run PERMANOVA on a distance matrix with grouping metadata.")
def distance_matrix_stats(distance_matrix: List[List[float]], ids: List[str], grouping: List[str], permutations: int = 99) -> Dict[str, Any]:
    """
    Execute PERMANOVA statistical test.

    Args:
        distance_matrix: Square distance matrix.
        ids: IDs corresponding to matrix rows/columns.
        grouping: Group labels aligned to IDs.
        permutations: Number of permutations.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        import numpy as np
        import pandas as pd
        from skbio.stats.distance import DistanceMatrix, permanova

        arr = np.asarray(distance_matrix, dtype=float)
        if arr.shape[0] != arr.shape[1]:
            raise ValueError("distance_matrix must be square")
        if len(ids) != arr.shape[0]:
            raise ValueError("len(ids) must match matrix dimension")
        if len(grouping) != len(ids):
            raise ValueError("len(grouping) must match len(ids)")

        dm = DistanceMatrix(arr, ids=ids)
        md = pd.DataFrame({"group": grouping}, index=ids)
        res = permanova(dm, md, column="group", permutations=permutations)
        return _ok(dict(res))
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="pcoa_analysis", description="Run PCoA ordination on a distance matrix.")
def pcoa_analysis(distance_matrix: List[List[float]], ids: List[str], dimensions: int = 3) -> Dict[str, Any]:
    """
    Run principal coordinates analysis.

    Args:
        distance_matrix: Square distance matrix.
        ids: IDs for matrix rows/columns.
        dimensions: Number of principal coordinate axes to return.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        import numpy as np
        from skbio.stats.distance import DistanceMatrix
        from skbio.stats.ordination import pcoa

        arr = np.asarray(distance_matrix, dtype=float)
        dm = DistanceMatrix(arr, ids=ids)
        ord_res = pcoa(dm)
        coords = ord_res.samples.iloc[:, :dimensions]
        return _ok(
            {
                "eigenvalues": ord_res.eigvals.iloc[:dimensions].tolist(),
                "proportion_explained": ord_res.proportion_explained.iloc[:dimensions].tolist(),
                "coordinates": coords.to_dict(orient="index"),
            }
        )
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="newick_tree_summary", description="Parse a Newick tree and return structural summary.")
def newick_tree_summary(newick: str) -> Dict[str, Any]:
    """
    Parse Newick and summarize topology.

    Args:
        newick: Newick tree string.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        from io import StringIO
        from skbio import TreeNode

        tree = TreeNode.read(StringIO(newick))
        tips = [t.name for t in tree.tips()]
        result = {
            "rooted": tree.is_root(),
            "tip_count": len(tips),
            "tips": tips,
            "ascii_art": tree.ascii_art(),
        }
        return _ok(result)
    except Exception as exc:
        return _err(exc)


@mcp.tool(name="io_sniff_format", description="Infer supported file format from path using scikit-bio IO sniff.")
def io_sniff_format(path: str) -> Dict[str, Any]:
    """
    Sniff file format using skbio.io.

    Args:
        path: Path to an input file.

    Returns:
        A dictionary with success/result/error fields.
    """
    try:
        import skbio.io as sio

        fmt = sio.sniff(path)
        return _ok({"path": path, "sniff_result": fmt})
    except Exception as exc:
        return _err(exc)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()