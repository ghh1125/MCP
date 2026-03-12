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
import pysam
from pysam import samtools as pysam_samtools
from pysam import bcftools as pysam_bcftools


mcp = FastMCP("pysam_mcp_service")


def _ok(result: Any) -> Dict[str, Any]:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> Dict[str, Any]:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="get_pysam_version", description="Get installed pysam version information.")
def get_pysam_version() -> Dict[str, Any]:
    """
    Return pysam version metadata.

    Returns:
        Dict with success/result/error where result includes pysam and htslib versions when available.
    """
    try:
        result = {
            "pysam_version": getattr(pysam, "__version__", None),
            "htslib_version": getattr(pysam, "__samtools_version__", None),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="index_bam", description="Create BAM/CRAM index using pysam.index.")
def index_bam(path: str, force: bool = False) -> Dict[str, Any]:
    """
    Build an index for a BAM/CRAM file.

    Parameters:
        path: Path to BAM/CRAM file.
        force: Overwrite existing index if True.

    Returns:
        Dict with success/result/error.
    """
    try:
        if force:
            pysam.index("-f", path)
        else:
            pysam.index(path)
        return _ok({"indexed": path})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="faidx_fasta", description="Create FASTA index using pysam.faidx.")
def faidx_fasta(path: str) -> Dict[str, Any]:
    """
    Build a .fai index for a FASTA file.

    Parameters:
        path: Path to FASTA file.

    Returns:
        Dict with success/result/error.
    """
    try:
        pysam.faidx(path)
        return _ok({"indexed": path})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_alignment_references", description="List references and lengths from an alignment file.")
def list_alignment_references(path: str, mode: str = "rb") -> Dict[str, Any]:
    """
    Read alignment header references.

    Parameters:
        path: Path to alignment file (BAM/CRAM/SAM).
        mode: Open mode, default 'rb'.

    Returns:
        Dict with success/result/error.
    """
    try:
        with pysam.AlignmentFile(path, mode) as af:
            refs = list(af.references or [])
            lens = list(af.lengths or [])
        return _ok({"references": refs, "lengths": lens})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="count_alignment_reads", description="Count reads in an alignment file or region.")
def count_alignment_reads(
    path: str,
    reference: Optional[str] = None,
    start: Optional[int] = None,
    end: Optional[int] = None,
    mode: str = "rb",
) -> Dict[str, Any]:
    """
    Count reads in an alignment file.

    Parameters:
        path: Path to BAM/CRAM/SAM.
        reference: Optional reference/contig name.
        start: Optional start coordinate (0-based).
        end: Optional end coordinate (0-based, exclusive).
        mode: Open mode, default 'rb'.

    Returns:
        Dict with success/result/error.
    """
    try:
        with pysam.AlignmentFile(path, mode) as af:
            if reference is None:
                count = af.count()
            else:
                count = af.count(contig=reference, start=start, stop=end)
        return _ok({"count": int(count)})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_vcf_contigs", description="List VCF/BCF contigs from header.")
def list_vcf_contigs(path: str, mode: str = "r") -> Dict[str, Any]:
    """
    List contigs defined in a variant file header.

    Parameters:
        path: Path to VCF/BCF file.
        mode: Open mode, default 'r'.

    Returns:
        Dict with success/result/error.
    """
    try:
        with pysam.VariantFile(path, mode) as vf:
            contigs = list(vf.header.contigs.keys())
        return _ok({"contigs": contigs})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="count_vcf_records", description="Count variant records in a VCF/BCF file.")
def count_vcf_records(path: str, mode: str = "r") -> Dict[str, Any]:
    """
    Count records in a variant file.

    Parameters:
        path: Path to VCF/BCF.
        mode: Open mode, default 'r'.

    Returns:
        Dict with success/result/error.
    """
    try:
        count = 0
        with pysam.VariantFile(path, mode) as vf:
            for _ in vf:
                count += 1
        return _ok({"count": count})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="tabix_index", description="Create tabix index for a bgzipped text file.")
def tabix_index(
    path: str,
    preset: str = "vcf",
    seq_col: Optional[int] = None,
    start_col: Optional[int] = None,
    end_col: Optional[int] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Build tabix index.

    Parameters:
        path: Path to bgzipped file.
        preset: Preset format (e.g., 'vcf', 'bed', 'gff', 'sam').
        seq_col: Sequence column (1-based), required when preset is not used.
        start_col: Start column (1-based), required when preset is not used.
        end_col: End column (1-based), optional.
        force: Overwrite index if True.

    Returns:
        Dict with success/result/error.
    """
    try:
        kwargs: Dict[str, Any] = {"preset": preset, "force": force}
        if seq_col is not None:
            kwargs["seq_col"] = seq_col
        if start_col is not None:
            kwargs["start_col"] = start_col
        if end_col is not None:
            kwargs["end_col"] = end_col
        idx = pysam.tabix_index(path, **kwargs)
        return _ok({"index_path": idx})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="samtools_command", description="Run a samtools subcommand exposed by pysam.samtools.")
def samtools_command(subcommand: str, arguments: List[str]) -> Dict[str, Any]:
    """
    Execute a samtools subcommand via pysam.samtools dispatcher.

    Parameters:
        subcommand: samtools command name (e.g., 'view', 'flagstat', 'idxstats').
        arguments: Positional command arguments.

    Returns:
        Dict with success/result/error.
    """
    try:
        fn = getattr(pysam_samtools, subcommand, None)
        if fn is None or not callable(fn):
            return _err(f"Unknown samtools subcommand: {subcommand}")
        output = fn(*arguments)
        return _ok({"output": output})
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="bcftools_command", description="Run a bcftools subcommand exposed by pysam.bcftools.")
def bcftools_command(subcommand: str, arguments: List[str]) -> Dict[str, Any]:
    """
    Execute a bcftools subcommand via pysam.bcftools dispatcher.

    Parameters:
        subcommand: bcftools command name (e.g., 'view', 'query', 'index').
        arguments: Positional command arguments.

    Returns:
        Dict with success/result/error.
    """
    try:
        fn = getattr(pysam_bcftools, subcommand, None)
        if fn is None or not callable(fn):
            return _err(f"Unknown bcftools subcommand: {subcommand}")
        output = fn(*arguments)
        return _ok({"output": output})
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()