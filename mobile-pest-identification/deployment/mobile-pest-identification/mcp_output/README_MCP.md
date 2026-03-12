# mobile-pest-identification MCP (Model Context Protocol) Service README

## 1) Project Introduction

`mobile-pest-identification` is a lightweight pest identification project centered around a mobile-oriented model configuration and Python inference workflow.

Main goals of this MCP (Model Context Protocol) service:
- Run pest identification from model/config + dataset metadata
- Provide a simple script-style execution path (`src/pest.py`)
- Reuse utility logic from `src/utils.py` for data parsing and helper operations
- Support IP102-related class/data files (`ip102_v1.1/*.txt`, `src/IP102_classes.txt`)

This repository is script-first (not a packaged Python library), so service integration is typically done by calling the script module or wrapping utility functions.

---

## 2) Installation Method

### Requirements
- Python 3.8+ recommended
- A virtual environment is strongly recommended
- Dependencies are listed in `requirements.txt` (install directly from file)

### Install Steps
1. Clone repository
   - `git clone https://github.com/wikilimo/mobile-pest-identification.git`
   - `cd mobile-pest-identification`

2. Create and activate virtual environment
   - macOS/Linux: `python -m venv .venv && source .venv/bin/activate`
   - Windows (PowerShell): `python -m venv .venv; .venv\Scripts\Activate.ps1`

3. Install dependencies
   - `pip install -U pip`
   - `pip install -r requirements.txt`

Note: If deep learning dependencies fail to install, verify your Python version and platform-compatible wheels (especially for torch-related stacks).

---

## 3) Quick Start

### Run the main workflow
- `python src/pest.py`

This is the primary inferred entry for local execution.

### Typical MCP (Model Context Protocol) service wrapping pattern
- Expose a `predict` service that internally calls logic in:
  - `src/pest.py` (orchestrator)
  - `src/utils.py` (pre/post-processing helpers)
- Load/validate:
  - `src/model/pest/mobile.yaml` (model config)
  - `src/IP102_classes.txt` (label mapping)
  - dataset split files in `ip102_v1.1/` if needed for validation/testing

---

## 4) Available Tools and Endpoints List

Because no formal API server is defined in the scanned files, below is the practical MCP (Model Context Protocol) service endpoint plan based on repository structure:

- `health`
  - Purpose: basic readiness/liveness check
  - Input: none
  - Output: service status, version, model-config availability

- `predict`
  - Purpose: pest inference endpoint
  - Input: image path/bytes (implementation choice), optional confidence threshold
  - Output: predicted pest class, confidence score, optional top-k results

- `labels`
  - Purpose: return class label metadata
  - Input: none
  - Output: parsed labels from `src/IP102_classes.txt`

- `config`
  - Purpose: inspect runtime model configuration
  - Input: none
  - Output: normalized fields loaded from `src/model/pest/mobile.yaml`

- `dataset_info` (optional)
  - Purpose: report train/val/test split statistics
  - Input: none
  - Output: counts/summary parsed from `ip102_v1.1/train.txt`, `val.txt`, `test.txt`

Current directly inferred command:
- `python src/pest.py`

---

## 5) Common Issues and Notes

- Dependency detection mismatch:
  - Analysis metadata reported `has_requirements_txt: False`, but repository tree includes `requirements.txt`.
  - Always trust actual repository files and install from `requirements.txt`.

- Script-first architecture:
  - No `setup.py`, `pyproject.toml`, or formal package exports detected.
  - For production MCP (Model Context Protocol) service use, add a thin API wrapper (FastAPI/Flask or MCP server runtime).

- Import feasibility risk (medium):
  - Internal module organization may assume execution from repository root.
  - Run commands from root directory to avoid relative path issues.

- Model/runtime performance:
  - Mobile model config suggests edge-friendly behavior, but performance depends on backend and hardware.
  - Preload model once at service startup to reduce per-request latency.

- Data path handling:
  - Ensure file paths to YAML/classes/split files are absolute or root-relative and stable in deployment.

---

## 6) Reference Links or Documentation

- Repository:
  - https://github.com/wikilimo/mobile-pest-identification

- Key files:
  - `README.md`
  - `requirements.txt`
  - `src/pest.py`
  - `src/utils.py`
  - `src/model/pest/mobile.yaml`
  - `src/IP102_classes.txt`
  - `ip102_v1.1/train.txt`, `ip102_v1.1/val.txt`, `ip102_v1.1/test.txt`

If you want, I can also generate a ready-to-use MCP (Model Context Protocol) service skeleton (tool schema + endpoint contracts) aligned to this repo’s structure.