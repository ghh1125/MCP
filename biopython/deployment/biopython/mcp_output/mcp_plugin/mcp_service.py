import os
import sys
from io import StringIO
from typing import List, Optional, Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
from Bio import SeqIO, AlignIO, Align
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord


mcp = FastMCP("biopython_core_service")


@mcp.tool(
    name="seqio_parse_text",
    description="Parse sequence records from text using Bio.SeqIO.parse.",
)
def seqio_parse_text(format_name: str, data: str) -> Dict[str, Any]:
    """
    Parse sequence records from in-memory text content.

    Parameters:
    - format_name: Sequence file format (e.g., 'fasta', 'genbank').
    - data: Raw text content containing one or more records.

    Returns:
    - dict with success/result/error.
    """
    try:
        handle = StringIO(data)
        records = list(SeqIO.parse(handle, format_name))
        result = [
            {
                "id": rec.id,
                "name": rec.name,
                "description": rec.description,
                "seq": str(rec.seq),
                "length": len(rec.seq),
            }
            for rec in records
        ]
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="seqio_read_text",
    description="Read exactly one sequence record from text using Bio.SeqIO.read.",
)
def seqio_read_text(format_name: str, data: str) -> Dict[str, Any]:
    """
    Read a single sequence record from in-memory text content.

    Parameters:
    - format_name: Sequence file format.
    - data: Raw text content containing exactly one record.

    Returns:
    - dict with success/result/error.
    """
    try:
        handle = StringIO(data)
        rec = SeqIO.read(handle, format_name)
        result = {
            "id": rec.id,
            "name": rec.name,
            "description": rec.description,
            "seq": str(rec.seq),
            "length": len(rec.seq),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="seqio_write_fasta",
    description="Write sequence records to FASTA text using Bio.SeqIO.write.",
)
def seqio_write_fasta(
    sequences: List[str],
    ids: Optional[List[str]] = None,
    descriptions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Create FASTA text from provided sequences.

    Parameters:
    - sequences: List of sequence strings.
    - ids: Optional list of IDs matching sequence count.
    - descriptions: Optional list of descriptions matching sequence count.

    Returns:
    - dict with success/result/error.
    """
    try:
        if ids is not None and len(ids) != len(sequences):
            raise ValueError("Length of ids must match length of sequences")
        if descriptions is not None and len(descriptions) != len(sequences):
            raise ValueError("Length of descriptions must match length of sequences")

        records = []
        for i, seq_text in enumerate(sequences):
            rec_id = ids[i] if ids is not None else f"seq_{i+1}"
            rec_desc = descriptions[i] if descriptions is not None else rec_id
            records.append(SeqRecord(Seq(seq_text), id=rec_id, description=rec_desc))

        out = StringIO()
        SeqIO.write(records, out, "fasta")
        return {"success": True, "result": out.getvalue(), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="alignio_parse_text",
    description="Parse alignments from text using Bio.AlignIO.parse.",
)
def alignio_parse_text(format_name: str, data: str) -> Dict[str, Any]:
    """
    Parse multiple alignments from in-memory text content.

    Parameters:
    - format_name: Alignment format (e.g., 'clustal', 'stockholm', 'phylip').
    - data: Raw text content containing one or more alignments.

    Returns:
    - dict with success/result/error.
    """
    try:
        handle = StringIO(data)
        aligns = list(AlignIO.parse(handle, format_name))
        result = [
            {
                "num_sequences": len(aln),
                "alignment_length": aln.get_alignment_length(),
                "ids": [rec.id for rec in aln],
            }
            for aln in aligns
        ]
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="alignio_read_text",
    description="Read exactly one alignment from text using Bio.AlignIO.read.",
)
def alignio_read_text(format_name: str, data: str) -> Dict[str, Any]:
    """
    Read a single alignment from in-memory text content.

    Parameters:
    - format_name: Alignment format.
    - data: Raw text content containing exactly one alignment.

    Returns:
    - dict with success/result/error.
    """
    try:
        handle = StringIO(data)
        aln = AlignIO.read(handle, format_name)
        result = {
            "num_sequences": len(aln),
            "alignment_length": aln.get_alignment_length(),
            "ids": [rec.id for rec in aln],
            "rows": [str(rec.seq) for rec in aln],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="align_pairwise_global",
    description="Run pairwise global alignment using Bio.Align.PairwiseAligner.",
)
def align_pairwise_global(
    sequence_a: str,
    sequence_b: str,
    match_score: float = 1.0,
    mismatch_score: float = 0.0,
    open_gap_score: float = -1.0,
    extend_gap_score: float = -0.5,
) -> Dict[str, Any]:
    """
    Perform global pairwise alignment with configurable scoring.

    Parameters:
    - sequence_a: First sequence.
    - sequence_b: Second sequence.
    - match_score: Score for matching characters.
    - mismatch_score: Score for mismatching characters.
    - open_gap_score: Gap opening score.
    - extend_gap_score: Gap extension score.

    Returns:
    - dict with success/result/error.
    """
    try:
        aligner = Align.PairwiseAligner()
        aligner.mode = "global"
        aligner.match_score = match_score
        aligner.mismatch_score = mismatch_score
        aligner.open_gap_score = open_gap_score
        aligner.extend_gap_score = extend_gap_score

        alignments = aligner.align(sequence_a, sequence_b)
        best = alignments[0]
        result = {
            "score": float(best.score),
            "num_alignments": len(alignments),
            "alignment": str(best),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="align_pairwise_local",
    description="Run pairwise local alignment using Bio.Align.PairwiseAligner.",
)
def align_pairwise_local(
    sequence_a: str,
    sequence_b: str,
    match_score: float = 1.0,
    mismatch_score: float = 0.0,
    open_gap_score: float = -1.0,
    extend_gap_score: float = -0.5,
) -> Dict[str, Any]:
    """
    Perform local pairwise alignment with configurable scoring.

    Parameters:
    - sequence_a: First sequence.
    - sequence_b: Second sequence.
    - match_score: Score for matching characters.
    - mismatch_score: Score for mismatching characters.
    - open_gap_score: Gap opening score.
    - extend_gap_score: Gap extension score.

    Returns:
    - dict with success/result/error.
    """
    try:
        aligner = Align.PairwiseAligner()
        aligner.mode = "local"
        aligner.match_score = match_score
        aligner.mismatch_score = mismatch_score
        aligner.open_gap_score = open_gap_score
        aligner.extend_gap_score = extend_gap_score

        alignments = aligner.align(sequence_a, sequence_b)
        best = alignments[0]
        result = {
            "score": float(best.score),
            "num_alignments": len(alignments),
            "alignment": str(best),
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()