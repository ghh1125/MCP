# SPM MCP (Model Context Protocol) Service README

## 1) Project Introduction

SPM is a lightweight sequence pattern matching utility focused on searching peptide/query sequences against a UniProt-style FASTA database and producing ranked results.  
This MCP (Model Context Protocol) service wraps the repository’s core script logic to expose practical sequence-search capabilities for downstream automation.

Main capabilities:
- Load and parse UniProt FASTA data
- Search query peptide/sequence patterns in a database
- Score/rank matches by sequence volume-related logic
- Export ranked output (example artifact: `output/test1_ranked.txt`)

Repository: https://github.com/YanLab-Westlake/SPM

---

## 2) Installation Method

This repository does not provide `requirements.txt`, `pyproject.toml`, or `setup.py`. Use a minimal Python 3 environment.

Recommended setup:
1. Install Python 3.8+ (3.x required)
2. Clone/download the repo
3. (Optional) Create a virtual environment
4. Run the script directly

Typical commands:
- `python -m venv .venv`
- `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
- `python scripts/SequencePatternMatching.py`

Notes:
- No explicit third-party dependencies were detected.
- If your environment differs, validate local Python path and file encodings.

---

## 3) Quick Start

Core module:
- `scripts/SequencePatternMatching.py`

Detected main functions:
- `loadUniprotDB(db_fasta)`
- `peptideSearching(db_fasta, query_seq, output_file)`
- `volumeScoring(query_seq_volume, uniprot_info, db_seq)`

Typical usage flow:
1. Prepare a FASTA database file (`db_fasta`)
2. Provide a query sequence (`query_seq`)
3. Run `peptideSearching(...)` to generate ranked output
4. (Optional) Use `loadUniprotDB(...)` and `volumeScoring(...)` for custom pipelines

Script-style execution:
- `python scripts/SequencePatternMatching.py`

Expected result:
- Ranked match output similar to `output/test1_ranked.txt`

---

## 4) Available Tools and Endpoints List

For this MCP (Model Context Protocol) service, expose the following service tools/endpoints:

- `load_uniprot_db`
  - Maps to: `loadUniprotDB(db_fasta)`
  - Purpose: Load and parse UniProt FASTA records

- `peptide_search`
  - Maps to: `peptideSearching(db_fasta, query_seq, output_file)`
  - Purpose: Run sequence pattern matching and write ranked results

- `volume_score`
  - Maps to: `volumeScoring(query_seq_volume, uniprot_info, db_seq)`
  - Purpose: Compute score contribution for candidate sequence ranking

- `run_sequence_pattern_matching` (wrapper endpoint)
  - Maps to script-level flow in `SequencePatternMatching.py`
  - Purpose: One-call execution from input FASTA/query to output ranking file

---

## 5) Common Issues and Notes

- Packaging metadata is missing  
  No official installable package config is provided; run as script/module in-place.

- Import feasibility is moderate  
  Analysis indicates script-first design. Prefer CLI/script execution if direct imports fail in your runtime.

- Input data quality matters  
  Ensure FASTA format is valid and query sequence format matches expected logic.

- File paths and permissions  
  Provide writable output paths (for ranked result files).

- Performance considerations  
  Larger FASTA databases may increase runtime. Consider batching queries or pre-filtering databases.

- MCP (Model Context Protocol) integration note  
  Since native MCP descriptors are not included, define a thin adapter layer that maps MCP (Model Context Protocol) tool calls to the three core functions above.

---

## 6) Reference Links or Documentation

- GitHub repository: https://github.com/YanLab-Westlake/SPM
- Core script: `scripts/SequencePatternMatching.py`
- Example output: `output/test1_ranked.txt`
- Existing repository README: `README.md`