# Open Babel MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps **Open Babel** for practical cheminformatics workflows, with a focus on:

- Molecular format conversion (SMILES, SDF, MOL, PDB, InChI, etc.)
- Descriptor/fingerprint generation
- Structure normalization and basic processing
- Batch processing through CLI-driven execution (`obabel`)

Because Python importability can vary by build, this service is designed to prefer stable **CLI black-box execution** (`obabel`) and optionally use Python bindings when available.

---

## 2) Installation Method

### System dependencies

- C++ build toolchain
- CMake
- Open Babel core library and CLI (`obabel`) installed and available in `PATH`

### Build Open Babel (typical)

- Clone: `https://github.com/openbabel/openbabel`
- Configure/build/install with CMake
- Verify:
  - `obabel -V` returns a version
  - Optional: Python bindings built via `scripts/python/setup.py` (build-dependent)

### Python-side notes

This repository does not expose a top-level modern Python package config at root (no root `requirements.txt` / `pyproject.toml` detected in analysis). If you need Python bindings, use the Open Babel binding workflow from `scripts/python/`.

---

## 3) Quick Start

### Minimal service flow

1. Accept user molecule input (string/file).
2. Call `obabel` with requested input/output format and options.
3. Return converted content, metadata, and execution logs/errors.

### Example usage patterns

- Convert SMILES to SDF
- Convert SDF to canonical SMILES
- Generate fingerprints/descriptors from input molecules
- Batch convert a directory of structure files

### Recommended execution strategy

- **Primary**: subprocess call to `obabel` (most robust across environments)
- **Fallback**: Python `openbabel/pybel` import only if confirmed available

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoints for this service:

- `health_check`
  - Confirms `obabel` availability/version and runtime readiness.

- `convert_molecule`
  - Single conversion between chemical formats.
  - Inputs: `input_format`, `output_format`, molecule content or file path, options.
  - Output: converted molecule text/file reference.

- `batch_convert`
  - Bulk file conversion.
  - Inputs: source path/pattern, target format, optional flags.
  - Output: converted file list and per-file status.

- `generate_fingerprint`
  - Computes molecular fingerprints using Open Babel capabilities.
  - Inputs: molecule + fingerprint type/options.
  - Output: fingerprint representation.

- `compute_descriptors`
  - Returns molecular descriptors available via Open Babel.
  - Inputs: molecule + descriptor selection.
  - Output: key-value descriptor map.

- `normalize_structure`
  - Standardizes molecule representation (e.g., canonicalization steps supported by `obabel` flags).
  - Inputs: molecule, normalization options.
  - Output: normalized structure.

- `get_supported_formats`
  - Lists readable/writable formats from current Open Babel build.

- `get_supported_services`
  - Lists enabled service operations based on installed binary/features.

---

## 5) Common Issues and Notes

- **`obabel` not found**
  - Ensure Open Babel is installed and executable is in `PATH`.
  - In containerized deployments, pin absolute executable path.

- **Feature mismatch across machines**
  - Available formats and capabilities depend on build options and linked libraries.
  - Always expose `get_supported_formats` at runtime.

- **Python bindings unavailable**
  - Expected in many environments; rely on CLI mode by default.

- **InChI and format-specific behavior**
  - InChI and some formats may require extra build support.
  - Validate with startup checks and capability reporting.

- **Performance**
  - Prefer batch operations for large jobs.
  - Stream file-based conversions for large molecules/sets instead of large in-memory payloads.

- **Reliability**
  - Return raw stderr/stdout snippets for troubleshooting.
  - Use deterministic flags where possible for reproducible output.

---

## 6) Reference Links and Documentation

- Open Babel repository: https://github.com/openbabel/openbabel
- Open Babel main docs/README (in repo): `README.md`
- Python examples:
  - `scripts/python/examples/`
  - `scripts/python/openbabel/pybel.py`
- Tests and format coverage:
  - `test/`
- Build configuration:
  - `CMakeLists.txt`
  - `.github/workflows/build_cmake.yml`

---

## Recommended Default for This MCP (Model Context Protocol) Service

Given current analysis (import feasibility low-to-medium), run this service in **CLI-first mode** using `obabel`, with Python binding support treated as optional enhancement.