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

try:
    import biotite
    import biotite.sequence as bseq
    import biotite.sequence.align as balign
    import biotite.sequence.io.fasta as fasta
    import biotite.sequence.io.fastq as fastq
    import biotite.database.uniprot as uniprot
    import biotite.database.rcsb as rcsb
except Exception:
    biotite = None
    bseq = None
    balign = None
    fasta = None
    fastq = None
    uniprot = None
    rcsb = None

mcp = FastMCP("biotite_service")


@mcp.tool(name="get_biotite_version", description="Get installed biotite version.")
def get_biotite_version() -> Dict[str, Any]:
    """
    Return the Biotite package version.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if biotite is None:
            raise ImportError("biotite package is not available")
        return {"success": True, "result": biotite.__version__, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="create_protein_sequence", description="Create a protein sequence from one-letter symbols.")
def create_protein_sequence(sequence: str) -> Dict[str, Any]:
    """
    Create a ProteinSequence object from an amino-acid sequence string.

    Parameters:
        sequence (str): Protein sequence in one-letter code.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if bseq is None:
            raise ImportError("biotite.sequence is not available")
        seq_obj = bseq.ProteinSequence(sequence)
        return {"success": True, "result": str(seq_obj), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="create_nucleotide_sequence", description="Create a nucleotide sequence.")
def create_nucleotide_sequence(sequence: str) -> Dict[str, Any]:
    """
    Create a NucleotideSequence object.

    Parameters:
        sequence (str): DNA/RNA sequence string.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if bseq is None:
            raise ImportError("biotite.sequence is not available")
        seq_obj = bseq.NucleotideSequence(sequence)
        return {"success": True, "result": str(seq_obj), "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="align_pairwise_protein", description="Perform pairwise global protein alignment.")
def align_pairwise_protein(
    seq1: str,
    seq2: str,
    matrix_name: str = "BLOSUM62",
    gap_penalty: int = -10,
    terminal_penalty: bool = False,
) -> Dict[str, Any]:
    """
    Run pairwise sequence alignment for two protein sequences.

    Parameters:
        seq1 (str): First protein sequence.
        seq2 (str): Second protein sequence.
        matrix_name (str): Substitution matrix name.
        gap_penalty (int): Gap penalty value.
        terminal_penalty (bool): Whether terminal gaps are penalized.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if bseq is None or balign is None:
            raise ImportError("biotite sequence alignment modules are not available")

        s1 = bseq.ProteinSequence(seq1)
        s2 = bseq.ProteinSequence(seq2)
        matrix = balign.SubstitutionMatrix.std_protein_matrix(matrix_name)

        alignments = balign.align_optimal(
            s1,
            s2,
            matrix,
            gap_penalty=gap_penalty,
            terminal_penalty=terminal_penalty,
        )
        if not alignments:
            return {"success": True, "result": {"score": None, "trace": None}, "error": None}

        best = alignments[0]
        result = {"score": int(best.score), "trace": best.trace.tolist()}
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="read_fasta", description="Read sequences from a FASTA file.")
def read_fasta(file_path: str) -> Dict[str, Any]:
    """
    Read FASTA records from a local file.

    Parameters:
        file_path (str): Path to FASTA file.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if fasta is None:
            raise ImportError("biotite.sequence.io.fasta is not available")
        fasta_file = fasta.FastaFile.read(file_path)
        records = []
        for header, seq in fasta_file.items():
            records.append({"header": header, "sequence": str(seq)})
        return {"success": True, "result": records, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="read_fastq", description="Read sequence records from a FASTQ file.")
def read_fastq(file_path: str, offset: int = 33) -> Dict[str, Any]:
    """
    Read FASTQ records from a local file.

    Parameters:
        file_path (str): Path to FASTQ file.
        offset (int): Quality score ASCII offset.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if fastq is None:
            raise ImportError("biotite.sequence.io.fastq is not available")
        fastq_file = fastq.FastqFile.read(file_path, offset=offset)
        records = []
        for identifier, (seq, quality) in fastq_file.items():
            records.append(
                {
                    "id": identifier,
                    "sequence": str(seq),
                    "quality": [int(q) for q in quality],
                }
            )
        return {"success": True, "result": records, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="query_uniprot", description="Search UniProt and return entry IDs.")
def query_uniprot(query: str, max_results: int = 25) -> Dict[str, Any]:
    """
    Query UniProt for entries.

    Parameters:
        query (str): UniProt query string.
        max_results (int): Maximum number of entry IDs to return.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if uniprot is None:
            raise ImportError("biotite.database.uniprot is not available")
        ids = uniprot.search(query)
        result = ids[:max_results] if isinstance(ids, list) else list(ids)[:max_results]
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="fetch_rcsb_structure", description="Download a structure file from RCSB PDB.")
def fetch_rcsb_structure(
    pdb_id: str,
    format: str = "pdbx",
    target_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Download a structure from RCSB.

    Parameters:
        pdb_id (str): PDB accession (e.g. '1CRN').
        format (str): File format, e.g. 'pdb', 'pdbx', or 'bcif'.
        target_path (Optional[str]): Optional output path.

    Returns:
        dict: Standard response dictionary with success/result/error.
    """
    try:
        if rcsb is None:
            raise ImportError("biotite.database.rcsb is not available")
        downloaded = rcsb.fetch(pdb_id, format=format, target_path=target_path)
        return {"success": True, "result": downloaded, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()