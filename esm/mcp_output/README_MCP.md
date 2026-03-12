# ESM MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the [facebookresearch/esm](https://github.com/facebookresearch/esm) toolkit as an MCP (Model Context Protocol) service for protein ML workflows.

Main capabilities:
- Load pretrained ESM/ESM-2 language models
- Parse FASTA/MSA inputs and tokenize sequences
- Extract embeddings (sequence-level or token-level)
- Run ESMFold structure prediction
- Run inverse-folding utilities (structure-conditioned scoring/sampling)
- Offer both Python-import execution and CLI fallback (`scripts/extract.py`, `scripts/fold.py`)

---

## 2) Installation

### Requirements
- Python >= 3.7
- Core: `torch`, `numpy`, `biopython`, `scipy`, `pandas`, `requests`, `tqdm`
- Optional (advanced/performance): `fairscale`, `hydra-core`, `omegaconf`, `deepspeed`, `pytorch-lightning`, OpenFold-compatible deps, CUDA runtime

### Install (typical)
- Clone repository and install:
  - `pip install -e .`
- Or install dependencies first, then package:
  - `pip install torch numpy biopython scipy pandas requests tqdm`
  - `pip install -e .`
- Conda users can use `environment.yml` as a base environment.

---

## 3) Quick Start

### A. Load model + alphabet (primary integration path)
Use `esm.pretrained.load_model_and_alphabet(...)` to initialize a model and tokenizer/alphabet for inference requests.

Typical flow:
1. Read sequences (e.g., FASTA) with `esm.data.read_fasta` / `parse_fasta`
2. Convert to tokens using `BatchConverter`
3. Run model forward pass
4. Return embeddings/logits in MCP (Model Context Protocol) response format

### B. ESMFold inference
Use `esm.esmfold.v1.pretrained.esmfold_v1()` for structure prediction requests.

### C. CLI fallback mode
If direct import fails in deployment, call:
- `python -m source.scripts.extract` for embedding extraction
- `python -m source.scripts.fold` for folding

This is useful for low-intrusion production integration.

---

## 4) Available Tools / Endpoints

Recommended MCP (Model Context Protocol) service endpoints:

- `health`
  - Check runtime availability, torch device, and model cache status.

- `models/list`
  - Return supported checkpoints (ESM-1, ESM-2, MSA Transformer, ESMFold if enabled).

- `sequence/tokenize`
  - Parse FASTA/raw sequence and return tokenized tensors/metadata.
  - Backed by `esm.data.Alphabet`, `BatchConverter`.

- `embeddings/extract`
  - Input: one or more protein sequences.
  - Output: per-sequence and/or per-token embeddings.
  - Backed by pretrained LM loaders and model forward pass.

- `fold/predict`
  - Input: amino-acid sequence.
  - Output: predicted structure (e.g., PDB text/path + confidence fields when available).
  - Backed by ESMFold loader/function.

- `inverse_folding/score`
  - Input: structure + candidate sequence.
  - Output: log-likelihood/score.
  - Backed by `esm.inverse_folding.util.score_sequence`.

- `inverse_folding/sample`
  - Input: structure (or complex context) + sampling params.
  - Output: sampled sequence(s).
  - Backed by `sample_sequence_in_complex`.

- `cli/extract` (fallback)
  - Executes extract script via subprocess for robust batch operation.

- `cli/fold` (fallback)
  - Executes fold script via subprocess for robust folding jobs.

---

## 5) Common Issues and Notes

- ESMFold is resource-heavy:
  - GPU strongly recommended for practical latency.
  - Ensure CUDA/driver compatibility with installed `torch`.
- First run may download checkpoints; plan cache persistence.
- Some advanced paths require extra optional dependencies (OpenFold-compatible stack, fairscale/deepspeed).
- For production MCP (Model Context Protocol) service:
  - Add request size limits (sequence length / batch size)
  - Add timeout + retry policies
  - Validate amino-acid alphabet before inference
- Import feasibility is generally good, but keep CLI fallback enabled for resilience.

---

## 6) References

- Repository: https://github.com/facebookresearch/esm
- Main package modules:
  - `esm.pretrained`
  - `esm.data`
  - `esm.model.esm2`
  - `esm.model.esm1`
  - `esm.model.msa_transformer`
  - `esm.esmfold.v1.pretrained`
  - `esm.inverse_folding.util`
- CLI scripts:
  - `scripts/extract.py`
  - `scripts/fold.py`
- Examples:
  - `examples/inverse_folding/`
  - `examples/variant-prediction/`
  - `examples/lm-design/`