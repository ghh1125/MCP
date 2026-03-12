# AiZynthFinder MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **AiZynthFinder** as an MCP (Model Context Protocol) backend for retrosynthesis workflows.  
It provides practical tools to:

- Load AiZynthFinder configuration and models
- Run retrosynthesis search for a target molecule (SMILES)
- Retrieve and analyze routes/reaction trees
- Export outputs for downstream LLM or application workflows

Core integration points in the codebase:

- `aizynthfinder.aizynthfinder.AiZynthFinder` (main orchestrator)
- `aizynthfinder.context.config.Configuration` (config bootstrap)
- `aizynthfinder.analysis.tree_analysis.TreeAnalysis` (post-search analysis)
- Search backends: MCTS, Retro*, Breadth-first, DFPN

---

## 2) Installation Method

### Prerequisites

- Python `>=3.10`
- Recommended system stack for chemistry/ML:
  - `rdkit`
  - `onnxruntime`
  - `numpy`, `pandas`, `PyYAML`, `networkx`

Optional (feature-dependent): `tensorflow`, `rdchiral`, `pymongo`, `paretoset`, `ipywidgets`, `jupyter`.

### Install

1. Create and activate a virtual environment.
2. Install AiZynthFinder and runtime dependencies.
3. Download/build required model and stock data.

Typical commands:

- `pip install aizynthfinder`
- `download_public_data` (fetch public assets)
- `make_stock ...` (prepare stock input if needed)

If you are packaging this as an MCP (Model Context Protocol) server, add your MCP runtime package (for example, FastMCP/SDK of choice) in the same environment.

---

## 3) Quick Start

### Minimal service flow

1. Load configuration (`Configuration`).
2. Initialize `AiZynthFinder`.
3. Set target SMILES.
4. Run tree search.
5. Collect routes and analysis (`TreeAnalysis`).

Example workflow (conceptual):

- Initialize with YAML config
- Run search for one molecule
- Return:
  - solved status
  - top-N routes
  - route scores
  - serialized reaction trees (JSON-ready)

Recommended MCP (Model Context Protocol) pattern:

- Keep a per-request “session” object in memory
- Expose separate tools for:
  - config/session initialization
  - run search
  - list routes
  - inspect route details
- Return compact JSON payloads for LLM consumption

---

## 4) Available Tools and Endpoints

Suggested MCP (Model Context Protocol) tools/endpoints for this service:

- `health_check`
  - Verify service readiness, dependency availability, and model paths.

- `init_session`
  - Inputs: config path or config object, optional backend override.
  - Output: session ID + loaded policy/stock/scorer summary.

- `run_retro_search`
  - Inputs: session ID, target SMILES, optional search limits.
  - Output: solved flag, iteration stats, route count.

- `get_routes`
  - Inputs: session ID, top_k, sort/scoring preference.
  - Output: ranked route list with summary metrics.

- `get_route_tree`
  - Inputs: session ID, route ID/index.
  - Output: serialized `ReactionTree` (nodes/reactions/metadata).

- `analyze_tree`
  - Inputs: session ID, analysis options.
  - Output: `TreeAnalysis` metrics, route quality indicators.

- `list_search_backends`
  - Output: available backends (MCTS, Retro*, Breadth-first, DFPN) and current selection.

- `export_results`
  - Inputs: session ID, format (json/csv-like summary path handling).
  - Output: export location or payload blob.

- `close_session`
  - Cleanup in-memory resources for the session.

Related native CLI utilities (useful for ops/debug):  
`aizynthcli`, `cat_aizynth_output`, `download_public_data`, `make_stock`.

---

## 5) Common Issues and Notes

- **RDKit installation issues**
  - Prefer conda-based install if pip wheels fail in your environment.

- **Model/data not found**
  - Ensure public data is downloaded and config paths are correct.

- **Slow runtime**
  - Retrosynthesis search can be compute-heavy; cap iterations/time per request.
  - Use queueing and per-request timeout in production.

- **Backend mismatch**
  - Some configs are tuned for MCTS; switching backend may affect quality/performance.

- **Optional dependency errors**
  - Install extras only when using corresponding features (e.g., TensorFlow policies, Mongo stock).

- **Concurrency**
  - Avoid unsafe shared mutable state; isolate sessions for multi-user MCP (Model Context Protocol) deployments.

- **Large payloads**
  - Return summarized route info by default; fetch full trees with a separate call.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/MolecularAI/aizynthfinder
- Main package entry: `aizynthfinder/aizynthfinder.py`
- CLI interface: `aizynthfinder/interfaces/aizynthcli.py`
- Analysis module: `aizynthfinder/analysis/tree_analysis.py`
- Search backends:
  - `aizynthfinder/search/mcts/`
  - `aizynthfinder/search/retrostar/`
  - `aizynthfinder/search/breadth_first/`
  - `aizynthfinder/search/dfpn/`
- Service extension examples: `services/README.md` (renamed from original services directory guidance)