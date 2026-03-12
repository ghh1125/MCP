import os
import sys
from typing import Dict, Any, List, Optional

source_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "source")
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

from deeptools import (
    bamCoverage,
    bamCompare,
    computeMatrix,
    computeMatrixOperations,
    plotHeatmap,
    plotProfile,
    multiBamSummary,
    multiBigwigSummary,
    plotCorrelation,
    plotPCA,
    plotCoverage,
    plotFingerprint,
    plotEnrichment,
    estimateReadFiltering,
    alignmentSieve,
    bigwigCompare,
    bigwigAverage,
    computeGCBias,
    correctGCBias,
    bamPEFragmentSize,
)

mcp = FastMCP("deeptools_mcp_service")


def _run_module_main(module: Any, argv: List[str]) -> Dict[str, Any]:
    try:
        old_argv = sys.argv[:]
        sys.argv = [module.__name__.split(".")[-1]] + argv
        if hasattr(module, "main"):
            result = module.main()
            return {"success": True, "result": result, "error": None}
        return {"success": False, "result": None, "error": f"Module {module.__name__} has no main()"}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}
    finally:
        sys.argv = old_argv


def _split_args(args: str) -> List[str]:
    if not args.strip():
        return []
    return [a for a in args.strip().split(" ") if a]


@mcp.tool(name="bam_coverage", description="Generate normalized coverage tracks from BAM files.")
def bam_coverage(args: str) -> Dict[str, Any]:
    """
    Run deepTools bamCoverage CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for bamCoverage.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(bamCoverage, _split_args(args))


@mcp.tool(name="bam_compare", description="Compare two BAM files to produce ratio/difference tracks.")
def bam_compare(args: str) -> Dict[str, Any]:
    """
    Run deepTools bamCompare CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for bamCompare.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(bamCompare, _split_args(args))


@mcp.tool(name="compute_matrix", description="Compute signal matrices around regions/reference points.")
def compute_matrix(args: str) -> Dict[str, Any]:
    """
    Run deepTools computeMatrix CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for computeMatrix.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(computeMatrix, _split_args(args))


@mcp.tool(name="compute_matrix_operations", description="Perform operations on computed matrix files.")
def compute_matrix_operations(args: str) -> Dict[str, Any]:
    """
    Run deepTools computeMatrixOperations CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for computeMatrixOperations.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(computeMatrixOperations, _split_args(args))


@mcp.tool(name="plot_heatmap", description="Render heatmaps from matrix files.")
def plot_heatmap(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotHeatmap CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotHeatmap.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotHeatmap, _split_args(args))


@mcp.tool(name="plot_profile", description="Render signal profiles from matrix files.")
def plot_profile(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotProfile CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotProfile.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotProfile, _split_args(args))


@mcp.tool(name="multi_bam_summary", description="Summarize multiple BAM files by bins/regions.")
def multi_bam_summary(args: str) -> Dict[str, Any]:
    """
    Run deepTools multiBamSummary CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for multiBamSummary.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(multiBamSummary, _split_args(args))


@mcp.tool(name="multi_bigwig_summary", description="Summarize multiple bigWig files by bins/regions.")
def multi_bigwig_summary(args: str) -> Dict[str, Any]:
    """
    Run deepTools multiBigwigSummary CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for multiBigwigSummary.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(multiBigwigSummary, _split_args(args))


@mcp.tool(name="plot_correlation", description="Plot correlation heatmap/scatter from summary results.")
def plot_correlation(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotCorrelation CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotCorrelation.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotCorrelation, _split_args(args))


@mcp.tool(name="plot_pca", description="Plot PCA from summary matrix.")
def plot_pca(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotPCA CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotPCA.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotPCA, _split_args(args))


@mcp.tool(name="plot_coverage", description="Coverage QC visualization over sample sets.")
def plot_coverage(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotCoverage CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotCoverage.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotCoverage, _split_args(args))


@mcp.tool(name="plot_fingerprint", description="ChIP/ATAC enrichment and complexity QC fingerprint plotting.")
def plot_fingerprint(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotFingerprint CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotFingerprint.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotFingerprint, _split_args(args))


@mcp.tool(name="plot_enrichment", description="Feature-centric enrichment plotting.")
def plot_enrichment(args: str) -> Dict[str, Any]:
    """
    Run deepTools plotEnrichment CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for plotEnrichment.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(plotEnrichment, _split_args(args))


@mcp.tool(name="estimate_read_filtering", description="Estimate read filtering effects under selected criteria.")
def estimate_read_filtering(args: str) -> Dict[str, Any]:
    """
    Run deepTools estimateReadFiltering CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for estimateReadFiltering.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(estimateReadFiltering, _split_args(args))


@mcp.tool(name="alignment_sieve", description="Filter and transform alignments based on flags/fragment criteria.")
def alignment_sieve(args: str) -> Dict[str, Any]:
    """
    Run deepTools alignmentSieve CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for alignmentSieve.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(alignmentSieve, _split_args(args))


@mcp.tool(name="bigwig_compare", description="Compare two bigWig tracks.")
def bigwig_compare_tool(args: str) -> Dict[str, Any]:
    """
    Run deepTools bigwigCompare CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for bigwigCompare.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(bigwigCompare, _split_args(args))


@mcp.tool(name="bigwig_average", description="Average multiple bigWig tracks.")
def bigwig_average_tool(args: str) -> Dict[str, Any]:
    """
    Run deepTools bigwigAverage CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for bigwigAverage.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(bigwigAverage, _split_args(args))


@mcp.tool(name="compute_gc_bias", description="Compute GC bias metrics.")
def compute_gc_bias(args: str) -> Dict[str, Any]:
    """
    Run deepTools computeGCBias CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for computeGCBias.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(computeGCBias, _split_args(args))


@mcp.tool(name="correct_gc_bias", description="Apply GC bias correction.")
def correct_gc_bias(args: str) -> Dict[str, Any]:
    """
    Run deepTools correctGCBias CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for correctGCBias.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(correctGCBias, _split_args(args))


@mcp.tool(name="bam_pe_fragment_size", description="Estimate paired-end fragment-size distributions.")
def bam_pe_fragment_size(args: str) -> Dict[str, Any]:
    """
    Run deepTools bamPEFragmentSize CLI-compatible entrypoint.

    Parameters:
    - args: Space-delimited command-line arguments for bamPEFragmentSize.

    Returns:
    - Dict with success/result/error.
    """
    return _run_module_main(bamPEFragmentSize, _split_args(args))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()