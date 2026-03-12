import os
import sys
from typing import List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

import torch
import esm
from scripts import extract as extract_script
from scripts import fold as fold_script

mcp = FastMCP("esm_service")


def _load_model(model_name: str):
    model, alphabet = esm.pretrained.load_model_and_alphabet(model_name)
    model.eval()
    return model, alphabet


@mcp.tool(
    name="list_pretrained_models",
    description="List available pretrained ESM model loader names from esm.pretrained.",
)
def list_pretrained_models() -> dict:
    """
    Return a list of callable pretrained model entrypoints available in esm.pretrained.

    Returns:
        dict: {
            "success": bool,
            "result": List[str] | None,
            "error": str | None
        }
    """
    try:
        names = []
        for name in dir(esm.pretrained):
            if name.startswith("_"):
                continue
            attr = getattr(esm.pretrained, name)
            if callable(attr):
                names.append(name)
        names.sort()
        return {"success": True, "result": names, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="embed_sequence",
    description="Generate per-sequence embedding for a protein sequence using an ESM model.",
)
def embed_sequence(
    sequence: str,
    model_name: str = "esm2_t6_8M_UR50D",
    repr_layer: int = 6,
    include_bos: bool = False,
) -> dict:
    """
    Generate a sequence embedding by averaging token representations.

    Args:
        sequence: Protein sequence string.
        model_name: Pretrained ESM model name.
        repr_layer: Representation layer index to extract.
        include_bos: Whether to include BOS token in averaging.

    Returns:
        dict: {
            "success": bool,
            "result": dict | None,
            "error": str | None
        }
    """
    try:
        sequence = sequence.strip()
        if not sequence:
            raise ValueError("sequence cannot be empty")

        model, alphabet = _load_model(model_name)
        batch_converter = alphabet.get_batch_converter()
        data = [("protein", sequence)]
        _, _, tokens = batch_converter(data)

        with torch.no_grad():
            out = model(tokens, repr_layers=[repr_layer], return_contacts=False)
        reps = out["representations"][repr_layer][0]

        start = 0 if include_bos else 1
        end = len(sequence) + 1
        seq_rep = reps[start:end].mean(0).cpu().tolist()

        return {
            "success": True,
            "result": {
                "model_name": model_name,
                "repr_layer": repr_layer,
                "embedding": seq_rep,
                "embedding_dim": len(seq_rep),
            },
            "error": None,
        }
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="score_sequence_log_likelihood",
    description="Compute mean log-likelihood score of a sequence under an ESM language model.",
)
def score_sequence_log_likelihood(
    sequence: str,
    model_name: str = "esm2_t6_8M_UR50D",
) -> dict:
    """
    Compute autoregressive-style pseudo log-likelihood by masked token scoring.

    Args:
        sequence: Protein sequence string.
        model_name: Pretrained ESM model name.

    Returns:
        dict: {
            "success": bool,
            "result": dict | None,
            "error": str | None
        }
    """
    try:
        sequence = sequence.strip()
        if not sequence:
            raise ValueError("sequence cannot be empty")

        model, alphabet = _load_model(model_name)
        batch_converter = alphabet.get_batch_converter()
        _, _, tokens = batch_converter([("protein", sequence)])

        token_ids = tokens[0].clone()
        mask_idx = alphabet.mask_idx
        log_probs: List[float] = []

        with torch.no_grad():
            for pos in range(1, len(sequence) + 1):
                masked = token_ids.clone()
                true_id = int(masked[pos].item())
                masked[pos] = mask_idx
                out = model(masked.unsqueeze(0), return_contacts=False)
                logits = out["logits"][0, pos]
                lp = torch.log_softmax(logits, dim=-1)[true_id].item()
                log_probs.append(lp)

        mean_lp = float(sum(log_probs) / len(log_probs))
        return {
            "success": True,
            "result": {
                "model_name": model_name,
                "sequence_length": len(sequence),
                "mean_log_likelihood": mean_lp,
                "token_log_likelihoods": log_probs,
            },
            "error": None,
        }
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="predict_structure_pdb",
    description="Run ESMFold to predict 3D structure and return PDB text.",
)
def predict_structure_pdb(
    sequence: str,
    model_name: str = "esmfold_v1",
    num_recycles: Optional[int] = None,
) -> dict:
    """
    Predict a protein structure with ESMFold and return PDB content.

    Args:
        sequence: Protein sequence string.
        model_name: ESMFold model name.
        num_recycles: Optional number of recycles for folding.

    Returns:
        dict: {
            "success": bool,
            "result": dict | None,
            "error": str | None
        }
    """
    try:
        sequence = sequence.strip()
        if not sequence:
            raise ValueError("sequence cannot be empty")

        model = esm.pretrained.esmfold_v1()
        model = model.eval()

        if num_recycles is not None:
            pdb_str = model.infer_pdb(sequence, num_recycles=num_recycles)
        else:
            pdb_str = model.infer_pdb(sequence)

        return {
            "success": True,
            "result": {
                "model_name": model_name,
                "pdb": pdb_str,
                "sequence_length": len(sequence),
            },
            "error": None,
        }
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="extract_embeddings_from_fasta",
    description="Run scripts.extract workflow over a FASTA file and output embeddings.",
)
def extract_embeddings_from_fasta(
    model_location: str,
    fasta_file: str,
    output_dir: str,
    repr_layers: List[int],
    include: str = "mean",
    truncation_seq_length: int = 1022,
    toks_per_batch: int = 4096,
    nogpu: bool = True,
) -> dict:
    """
    Call the repository extract script main routine programmatically.

    Args:
        model_location: Model name/path accepted by scripts.extract.
        fasta_file: Input FASTA file path.
        output_dir: Output directory path.
        repr_layers: Representation layers to export.
        include: Comma-separated include string (e.g., 'mean,per_tok').
        truncation_seq_length: Max sequence length.
        toks_per_batch: Tokens per batch.
        nogpu: Disable GPU usage when True.

    Returns:
        dict: {
            "success": bool,
            "result": str | None,
            "error": str | None
        }
    """
    try:
        extract_script.run(
            model_location=model_location,
            fasta_file=fasta_file,
            output_dir=output_dir,
            repr_layers=repr_layers,
            include=include.split(",") if include else ["mean"],
            truncation_seq_length=truncation_seq_length,
            toks_per_batch=toks_per_batch,
            nogpu=nogpu,
        )
        return {"success": True, "result": "embeddings_extracted", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(
    name="fold_fasta_sequences",
    description="Run scripts.fold workflow for FASTA input and write predicted structures.",
)
def fold_fasta_sequences(
    fasta_file: str,
    output_dir: str,
    num_recycles: int = 4,
    max_tokens_per_batch: int = 1024,
    chunk_size: int = 128,
    cpu_only: bool = True,
) -> dict:
    """
    Call the repository fold script main routine programmatically.

    Args:
        fasta_file: Input FASTA path.
        output_dir: Output directory for PDB files.
        num_recycles: Number of recycles.
        max_tokens_per_batch: Batch token cap.
        chunk_size: Axial attention chunk size.
        cpu_only: Force CPU inference.

    Returns:
        dict: {
            "success": bool,
            "result": str | None,
            "error": str | None
        }
    """
    try:
        fold_script.run(
            fasta=fasta_file,
            output_dir=output_dir,
            num_recycles=num_recycles,
            max_tokens_per_batch=max_tokens_per_batch,
            chunk_size=chunk_size,
            cpu_only=cpu_only,
        )
        return {"success": True, "result": "folding_completed", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()