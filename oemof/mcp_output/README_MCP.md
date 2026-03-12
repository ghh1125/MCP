# oemof MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository provides the base `oemof` Python package with a minimal CLI entrypoint.  
For an MCP (Model Context Protocol) service integration, the practical approach is to wrap the existing CLI/module entrypoints as callable service operations.

Main integration surface:
- `oemof.cli.main` (primary)
- `python -m oemof` via `oemof.__main__.main` (module entrypoint)

Given the scanned repository snapshot, this package currently exposes a lightweight command interface rather than a large in-repo API surface.

## 2) Installation Method

### Requirements
- Python 3.8+ (recommended)
- `setuptools` (required)
- Optional dev/docs tooling seen in repo: `tox`, `Sphinx`, `pytest` (mainly for development/testing)

### Install from source
1. Clone repository:
   `git clone https://github.com/oemof/oemof.git`
2. Enter directory:
   `cd oemof`
3. Install:
   `pip install .`

### Developer install (optional)
- `pip install -e .`
- If needed for CI/docs workflows, also install from `ci/requirements.txt` and `docs/requirements.txt`.

## 3) Quick Start

### Run as module
`python -m oemof`

### Call CLI main function from Python
`from oemof.cli import main; main()`

### MCP (Model Context Protocol) service wrapping pattern
Create a thin MCP (Model Context Protocol) service method that delegates to:
- `oemof.cli.main()` for command execution
- or subprocess call to `python -m oemof` for stronger process isolation

Recommended: start with subprocess wrapping for safer error capture and simpler timeout control.

## 4) Available Tools and Endpoints List

Based on current analysis, only a minimal command surface is discoverable.

- `run_oemof_cli`
  - Purpose: Execute `oemof` CLI through module entrypoint.
  - Backing target: `python -m oemof` or `oemof.cli.main`.
  - Input: CLI-style arguments (if supported by runtime implementation).
  - Output: Process/result text, exit status, error details.

- `health_check`
  - Purpose: Verify service availability and `oemof` importability.
  - Backing target: `import oemof` and optional version check.
  - Output: `ok`/`error`, environment metadata.

- `version_info`
  - Purpose: Return package/runtime version details for diagnostics.
  - Backing target: package metadata and Python runtime info.

Note: No additional stable subcommands were reliably identified from the provided scan metadata.

## 5) Common Issues and Notes

- Limited discovered API surface:
  The repository snapshot indicates minimal direct runtime modules (`__main__.py`, `cli.py`), so keep MCP (Model Context Protocol) service scope focused and thin.

- Argument compatibility:
  If wrapping `oemof.cli.main()` directly, ensure argument parsing behavior is validated in your environment.

- Environment mismatch:
  Prefer virtual environments to avoid dependency conflicts.

- Import feasibility:
  Automated assessment indicates moderate feasibility (~0.61). If direct import causes issues, use subprocess execution as fallback.

- Documentation gap:
  Deep analysis source failed in the provided report, so validate runtime behavior with local smoke tests before exposing production endpoints.

## 6) Reference Links or Documentation

- Repository: https://github.com/oemof/oemof
- Package entry module: `src/oemof/__main__.py`
- CLI module: `src/oemof/cli.py`
- Build/config:
  - `pyproject.toml`
  - `setup.cfg`
  - `setup.py`
- Test/dev orchestration: `tox.ini`
- Docs config: `docs/conf.py`