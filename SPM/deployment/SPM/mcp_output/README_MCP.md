# SPM MCP (Model Context Protocol) Service README

## 1) Project Introduction

SPM is a lightweight sequence pattern matching project centered on a single executable script:

- `scripts/SequencePatternMatching.py`

This MCP (Model Context Protocol) service wrapper is intended to expose that script as a practical developer-facing service for running sequence pattern matching and returning ranked results (for example, outputs similar to `output/test1_ranked.txt`).

Main function of the service:

- Execute sequence pattern matching jobs
- Return ranked matching results
- Support simple integration through MCP (Model Context Protocol) service endpoints

---

## 2) Installation Method

This repository does not include `requirements.txt`, `pyproject.toml`, or other package metadata.  
Minimum known dependency is Python runtime.

Recommended setup:

1. Install Python 3.9+ (3.10+ recommended)
2. Clone repository
3. (Optional) create virtual environment
4. Run script directly

Suggested commands:

- `git clone https://github.com/YanLab-Westlake/SPM.git`
- `cd SPM`
- `python -m venv .venv`
- `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
- `python scripts/SequencePatternMatching.py`

If runtime errors indicate missing libraries, install them with `pip install <package>` as needed.

---

## 3) Quick Start

Because the project is script-first (not a packaged Python module), the most reliable integration path is CLI-style execution from your MCP (Model Context Protocol) service.

Typical flow:

1. Receive input sequence/pattern parameters in your MCP (Model Context Protocol) request
2. Invoke `python scripts/SequencePatternMatching.py` (with your adapted arguments or input files)
3. Parse generated ranked output (e.g., under `output/`)
4. Return normalized JSON to clients

Minimal service usage pattern:

- Input: sequence data + matching configuration
- Processing: call script
- Output: ranked match list, score, and metadata (file path, run time, status)

---

## 4) Available Tools and Endpoints List

Based on current repository contents, define MCP (Model Context Protocol) services like below:

### `spm.run_match`
Runs sequence pattern matching job via `scripts/SequencePatternMatching.py`.

- Purpose: execute one matching task
- Input: sequence/pattern payload (or file references), optional runtime parameters
- Output: job status, ranked results (or output file reference)

### `spm.get_ranked_output`
Returns parsed ranked output from generated files (such as `output/test1_ranked.txt`).

- Purpose: read/parse result artifacts
- Input: output file path or job id
- Output: structured ranked entries

### `spm.health`
Basic health check endpoint for MCP (Model Context Protocol) service process.

- Purpose: operational monitoring
- Output: service status, Python runtime info, script path check

Note: These are practical MCP (Model Context Protocol) service endpoint recommendations derived from repository structure; the upstream project does not ship formal API endpoints.

---

## 5) Common Issues and Notes

- No formal dependency manifest is provided. Expect manual dependency resolution.
- Import feasibility is low-to-moderate; prefer subprocess/CLI invocation over direct Python imports.
- Script arguments are not formally documented in metadata; inspect `scripts/SequencePatternMatching.py` before production wiring.
- Ensure write permissions for output directories (e.g., `output/`).
- For large datasets, monitor execution time and memory usage in your MCP (Model Context Protocol) service runtime.
- Add timeout/retry and clear error mapping in service layer to improve reliability.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/YanLab-Westlake/SPM
- Core script: `scripts/SequencePatternMatching.py`
- Example output artifact: `output/test1_ranked.txt`
- MCP (Model Context Protocol): https://modelcontextprotocol.io/

If needed, create an internal service contract doc describing:
- request/response schema
- error codes
- output ranking field definitions
- operational limits (timeout, max input size)