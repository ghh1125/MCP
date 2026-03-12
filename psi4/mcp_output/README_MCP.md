# Psi4 MCP (Model Context Protocol) Service README

## 1) Introduction

This project provides an MCP (Model Context Protocol) service layer for **Psi4** (quantum chemistry engine), exposing practical, automation-friendly operations such as:

- Single-point energy calculations
- Gradient/property execution
- Schema-based task execution (QCSchema-style)
- Task planning and structured job orchestration

It is intended for developers who want to call Psi4 from MCP (Model Context Protocol) clients (agents, orchestration servers, workflow tools) without tightly coupling to Psi4 internals.

---

## 2) Installation

### Prerequisites

- Python 3.9+ (recommended)
- CMake toolchain (for compiled Psi4 components)
- A working Psi4 installation (conda recommended)
- Native scientific dependencies required by Psi4 core

### Recommended setup (conda first)

1. Install Psi4 in a dedicated environment (recommended by upstream):
   - Use official Psi4 install guidance from repository/docs.
2. Install your MCP (Model Context Protocol) service package:
   - `pip install -e .` (for local development)
   - or `pip install <your-mcp-service-package>`

### Notes

- This repository is build-heavy; pure `pip install psi4` may not match your platform/toolchain.
- If import of `psi4` fails, fix the compiled/runtime environment first before testing MCP (Model Context Protocol) endpoints.

---

## 3) Quick Start

### Minimal flow

1. Start MCP (Model Context Protocol) service process.
2. Call an endpoint such as `energy.compute` with:
   - molecule specification
   - method (e.g., HF/DFT)
   - basis
   - optional driver options
3. Receive structured result (energy value, metadata, errors).

### Example request shape (conceptual)

- `task`: `energy`
- `model.method`: `HF`
- `model.basis`: `cc-pVDZ`
- `molecule`: atoms, charge, multiplicity
- `options`: convergence, memory, threads

### Main integration points in Psi4

- `psi4.driver.driver` (core orchestration)
- `psi4.driver.schema_wrapper` (structured/schema execution)
- `psi4.driver.task_planner` (planning/multi-step execution)
- `psi4.run_psi4` (runtime/launcher behavior)

---

## 4) Available Tools / Endpoints

Suggested MCP (Model Context Protocol) endpoint set for this service:

- `health.check`  
  Returns service/runtime readiness (Python, Psi4 import, compiled libs).

- `psi4.version`  
  Returns Psi4 version/build/runtime details.

- `energy.compute`  
  Runs single-point energy calculation.

- `gradient.compute`  
  Runs gradient calculation.

- `properties.compute`  
  Runs selected molecular properties.

- `schema.run`  
  Executes structured schema input via Psi4 schema wrapper.

- `task.plan`  
  Builds execution plan for multi-step jobs (e.g., optimize → frequency).

- `task.run`  
  Executes a planned task graph/workflow.

- `options.list`  
  Lists supported/active Psi4 options exposed by service.

- `methods.list`  
  Lists available methods/basis families detected in runtime.

- `job.status`  
  Polls async job status (if service uses background execution).

- `job.cancel`  
  Cancels a running job.

---

## 5) Common Issues and Notes

- **Import issues (`import psi4`)**  
  Usually environment/toolchain related; verify conda env and native libs.

- **Large runtime footprint**  
  Psi4 is compute-heavy; set memory/threads explicitly per request.

- **Platform differences**  
  Linux/macOS are typically smoother than ad hoc Windows native builds.

- **Method availability varies**  
  Some capabilities depend on optional external components and build flags.

- **Performance**  
  Reuse long-lived worker processes for lower startup overhead.

- **Error handling**  
  Wrap Psi4 exceptions into structured MCP (Model Context Protocol) errors with actionable diagnostics (input validation, missing basis, SCF convergence, etc.).

---

## 6) References

- Psi4 repository: https://github.com/psi4/psi4
- Psi4 top-level docs/README (in repo): `README.md`
- Driver core modules:
  - `psi4/driver/driver.py`
  - `psi4/driver/schema_wrapper.py`
  - `psi4/driver/task_planner.py`
  - `psi4/run_psi4.py`
- Conda helper utility in repo:
  - `conda/psi4-path-advisor.py`

If you want, I can also generate a production-ready `mcp_service.yaml` endpoint contract and JSON request/response schemas aligned to this README.