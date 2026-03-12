# Sage MCP (Model Context Protocol) Service README

## 1) Introduction

This project provides an MCP (Model Context Protocol) service layer for working with the SageMath codebase and runtime.  
It is intended for developer workflows that need:

- Sage expression evaluation
- File/script execution
- Notebook/Jupyter integration
- Version and environment inspection
- Optional documentation build integration (`sage_docbuild`)

Given Sage’s size and native dependencies, this MCP (Model Context Protocol) service is best used in a prepared Sage environment (container, distro package, or full source build).

---

## 2) Installation

### Prerequisites

- Python 3.12+
- A working SageMath runtime (recommended: packaged Sage install or official container/dev environment)
- Optional for docs: Sphinx toolchain used by `sage_docbuild`
- Optional for notebooks: Jupyter/IPython stack

### Recommended setup flow

1. Install SageMath first (system package, conda-based environment, or source build).
2. Verify Sage is available in PATH.
3. Install your MCP (Model Context Protocol) host/runtime.
4. Register this service command in your MCP (Model Context Protocol) client config.

### Minimal verification

- `sage --version`
- `python -m sage_docbuild --help` (optional)

---

## 3) Quick Start

### Typical service actions

- Evaluate expression:
  - `eval`: run Sage expressions and return result
- Run script:
  - `run-file`: execute `.sage` or `.py` files
- Start notebook workflow:
  - `notebook`: launch Jupyter-backed Sage context
- Check version:
  - `version`: return Sage version info

### Example interaction flow

1. MCP (Model Context Protocol) client calls `version` to confirm environment.
2. Calls `eval` for lightweight math tasks.
3. Uses `run-file` for larger workflows or reproducible scripts.
4. Uses `notebook` when interactive exploration is required.

---

## 4) Tools / Endpoints

- `version`  
  Returns Sage runtime version and basic environment metadata.

- `eval`  
  Evaluates Sage code snippets/expressions in Sage runtime context.

- `run-file`  
  Executes Sage/Python files from disk.

- `notebook`  
  Starts notebook-oriented workflow using Sage kernel integration.

- `docbuild` (optional, via `python -m sage_docbuild`)  
  Builds Sage documentation (HTML/PDF workflows depending on toolchain).

- `bootstrap` (maintenance-oriented, source-build users)  
  Package/bootstrap utilities from `build/sage_bootstrap`.

---

## 5) Common Issues & Notes

- Heavy dependency footprint  
  Sage relies on many compiled backends (e.g., GAP, PARI, Singular, FLINT). Missing components can break specific operations.

- Import/runtime cost  
  Top-level Sage imports are large and can be slow; prefer targeted operations where possible.

- Environment mismatch  
  Python-only virtualenv without Sage system/runtime support is usually insufficient.

- Notebook startup failures  
  Usually due to missing Jupyter kernel setup or partial Sage installation.

- Performance  
  First-run latency can be high; warm environments/containers improve responsiveness.

- CI/container usage  
  Prefer reproducible devcontainer/docker workflows for consistent results across machines.

---

## 6) References

- Repository: https://github.com/sagemath/sage
- Main project README: `README.md` in repository root
- Docker notes: `docker/README.md`
- Build/bootstrap tooling: `build/sage_bootstrap/`
- Documentation builder entrypoint: `src/sage_docbuild/__main__.py`
- CLI modules:
  - `src/sage/cli/__main__.py`
  - `src/sage/cli/eval_cmd.py`
  - `src/sage/cli/run_file_cmd.py`
  - `src/sage/cli/notebook_cmd.py`
  - `src/sage/cli/version_cmd.py`