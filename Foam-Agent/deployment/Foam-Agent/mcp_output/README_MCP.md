# Foam-Agent MCP (Model Context Protocol) Service README

## 1) Project Introduction

Foam-Agent is an AI-assisted OpenFOAM workflow system.  
Its MCP (Model Context Protocol) service exposes practical simulation capabilities so clients (IDE agents, orchestration tools, or custom apps) can:

- plan a CFD case from natural-language requirements,
- generate or rewrite OpenFOAM input files,
- prepare meshes (including custom/Gmsh paths),
- run simulations locally or on HPC (Slurm),
- review errors and apply fixes,
- generate visualization scripts/results.

Core implementation is centered in `src/mcp/fastmcp_server.py`, with domain logic in `src/services/*`.

---

## 2) Installation Method

### Prerequisites

- Python >= 3.10
- System OpenFOAM runtime available in shell
- Recommended: Conda (repo provides `environment.yml`)
- For vector retrieval: `faiss` / `faiss-cpu`
- Optional integrations:
  - OpenAI/Hugging Face APIs
  - AWS usage tracking (`boto3`)
  - HPC Slurm tools (`sbatch`, `squeue`, `scancel`)
  - Visualization stack (PyVista / ParaView bindings)

### Setup (recommended)

1. Create environment from `environment.yml`
2. Activate environment
3. Initialize local database/index assets:
   - `python init_database.py`
4. Start MCP (Model Context Protocol) service:
   - `python src/mcp/start_mcp.py`

If you prefer pip-based setup, install core dependencies such as:
`fastmcp`, `pydantic`, `numpy`, `requests`, `PyYAML`, `faiss-cpu` (plus project-specific LLM/orchestration dependencies used by the repo).

---

## 3) Quick Start

### Run service

- Start server: `python src/mcp/start_mcp.py`
- Main orchestration (non-MCP path): `python src/main.py`
- Lightweight launcher: `python app.py`

### Typical MCP (Model Context Protocol) workflow

1. **Plan**: parse user requirement and choose reference case/strategy  
2. **Generate files**: create initial OpenFOAM case files and `Allrun` flow  
3. **Run simulation**: local or HPC execution  
4. **Review/apply fixes**: analyze logs and patch files  
5. **Visualize**: produce post-processing script/output

### Service-level scripts

- Database prep: `python init_database.py`
- Benchmark flow: `python foambench_main.py`

---

## 4) Available Tools and Endpoints List

The MCP (Model Context Protocol) server defines request/response models for these service endpoints:

- **Plan**
  - Request/Response: `PlanRequest` / `PlanResponse`
  - Purpose: convert requirement text to case plan, subtasks, and references.

- **Generate Files**
  - `GenerateFilesRequest` / `GenerateFilesResponse`
  - Purpose: initial case file generation and rewrite support.

- **Run Simulation**
  - `RunSimulationRequest` / `RunSimulationResponse`
  - Purpose: execute case locally or via HPC path.

- **Review**
  - `ReviewRequest` / `ReviewResponse`
  - Purpose: inspect errors/logs and create rewrite guidance.

- **Apply Fixes**
  - `ApplyFixesRequest` / `ApplyFixesResponse`
  - Purpose: apply planned modifications to problematic files.

- **Visualization**
  - `VisualizationRequest` / `VisualizationResponse`
  - Purpose: ensure `.foam` readiness and run/generated visualization scripts.

Related service modules:
- `src/services/plan.py`
- `src/services/input_writer.py`
- `src/services/mesh.py`
- `src/services/run_local.py`
- `src/services/run_hpc.py`
- `src/services/review.py`
- `src/services/visualization.py`

---

## 5) Common Issues and Notes

- **OpenFOAM not found**: ensure OpenFOAM environment is sourced in the runtime shell.
- **FAISS/index missing**: run `python init_database.py` before planning/retrieval-heavy flows.
- **HPC job failures**: verify Slurm commands are installed and accessible; confirm queue/account settings.
- **Timeouts on large cases**: increase run timeout/retry settings in run services.
- **Visualization errors**: check PyVista/ParaView compatibility and case output availability.
- **API-backed LLM features**: set required credentials/env vars before running generation/review paths.
- **Performance**: first run may be slower due to data loading/index warm-up.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/csml-rpi/Foam-Agent
- MCP (Model Context Protocol) server docs in repo: `src/mcp/README.md`
- Core server entry: `src/mcp/fastmcp_server.py`
- Orchestration entry: `src/main.py`
- Tests:
  - `tests/test_lid_driven_cavity_mcp.py`
  - `tests/test_lid_driven_cavity_services.py`