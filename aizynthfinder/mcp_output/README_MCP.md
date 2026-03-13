# AiZynthFinder MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **AiZynthFinder** as an MCP (Model Context Protocol) backend for retrosynthesis workflows.  
It provides developer-friendly tools to:

- Run retrosynthesis search from a target molecule (SMILES)
- Analyze and rank routes after search
- Manage stock and model-related operational tasks
- Optionally use CLI-based fallback when direct Python imports are constrained

Primary integration points in AiZynthFinder:

- `AiZynthFinder` (orchestration)
- `Configuration` (runtime config loading)
- `MctsSearchTree` (search engine)
- `TreeAnalysis` (route extraction and scoring)

---

## 2) Installation Method

### Requirements

- Python `>=3.9`
- Core libs: `rdkit`, `numpy`, `pandas`, `networkx`, `pyyaml`, `scipy`, `onnxruntime`
- Optional:
  - `tensorflow/keras` (some expansion/filter backends)
  - `pymongo` (Mongo utilities)
  - notebook/GUI plotting stack for interactive usage

### Install

1. Install AiZynthFinder from source or package.
2. Install MCP (Model Context Protocol) server runtime dependencies.
3. Ensure model/data assets are available (local paths or downloaded public data).

Typical operational commands in this ecosystem:

- `aizynthcli` (batch retrosynthesis)
- `download_public_data` (fetch public assets)
- `make_stock` (build stock artifacts)
- `cat_output` (inspect/merge outputs)

---

## 3) Quick Start

### Minimal workflow

1. Load AiZynthFinder configuration (policies, stock, scorers, search settings).
2. Create an `AiZynthFinder` instance.
3. Set target SMILES.
4. Run search (MCTS by default).
5. Use `TreeAnalysis` to extract/rank routes.
6. Return structured results via MCP (Model Context Protocol) tool responses.

### Example MCP (Model Context Protocol) usage flow

- `health_check` → verify runtime/dependencies
- `load_config` → parse config and validate resources
- `run_retrosynthesis` with target SMILES and limits (iterations/time)
- `analyze_routes` for ranking/summary
- `export_results` to JSON/CSV-like artifacts

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) tool set:

- `health_check`  
  Validate Python/runtime, key imports, and model/stock path availability.

- `load_config`  
  Load and validate AiZynthFinder configuration.

- `run_retrosynthesis`  
  Execute search for a target molecule; returns route candidates and search metadata.

- `analyze_routes`  
  Run post-processing with route ranking, scores, and route statistics.

- `get_search_status`  
  Return progress/status for long-running jobs.

- `list_scoring_strategies`  
  Show available scorer names from context/scoring collection.

- `list_expansion_strategies`  
  Show active expansion strategies from policy configuration.

- `build_stock`  
  Administrative helper around stock generation workflow (from molecular inputs).

- `download_public_data`  
  Operational helper to fetch public model/data assets.

- `run_cli_fallback`  
  Execute `aizynthcli` pipeline when import-mode integration is not suitable.

---

## 5) Common Issues and Notes

- **RDKit installation**: most common setup blocker; use a compatible Python environment.
- **Model/backend mismatch**: some policies require TensorFlow/Keras; ensure backend matches config.
- **Missing stock/models**: search quality depends heavily on valid stock and trained expansion/filter assets.
- **Performance**: MCTS can be expensive; control iterations, depth, and timeout in config.
- **Import vs CLI mode**: import integration is preferred; keep CLI fallback for isolated/sandboxed deployments.
- **Environment reproducibility**: pin dependency versions and keep config/data paths explicit.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/MolecularAI/aizynthfinder
- Core modules to review:
  - `aizynthfinder/aizynthfinder.py`
  - `aizynthfinder/context/config.py`
  - `aizynthfinder/search/mcts/search.py`
  - `aizynthfinder/analysis/tree_analysis.py`
  - `aizynthfinder/interfaces/aizynthcli.py`
  - `aizynthfinder/tools/make_stock.py`
- Existing project docs and changelog in repo root (`README.md`, `CHANGELOG.md`).

If you are packaging this as a standalone MCP (Model Context Protocol) service, keep tool interfaces thin, prefer structured JSON outputs, and expose config/search limits explicitly for safe operation.