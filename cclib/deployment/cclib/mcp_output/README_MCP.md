# cclib MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps **cclib** as an MCP (Model Context Protocol) backend for computational chemistry outputs.  
Its goal is to provide reliable, program-agnostic parsing and lightweight analysis tools for quantum chemistry log files.

Main capabilities:
- Parse outputs from major QC engines (Gaussian, ORCA, Q-Chem, NWChem, ADF, DALTON, Molpro, Psi4, Turbomole, xTB, etc.)
- Extract normalized attributes (energies, geometries, orbitals, charges, vibrations, excited states)
- Convert parsed data to common formats (cjson, molden, xyz, wfx)
- Run selected post-processing methods (population/orbital/density-related analyses)

---

## 2) Installation Method

### Requirements
Core Python dependencies:
- numpy
- scipy
- packaging
- periodictable

Optional integrations:
- pandas, ase, biopython, openbabel, psi4, pyquante, pyscf, horton

### Install
- Install from PyPI:
  - `pip install cclib`
- Or for development:
  - clone repo, then `pip install -e .`
- Optional extras should be installed separately as needed by specific services.

---

## 3) Quick Start

### Basic parse flow
Use the high-level I/O API:
- `cclib.io.ccopen(path)` → detect parser and open file
- `cclib.io.ccread(path)` → one-shot parse and return data object
- `cclib.io.ccwrite(data, outputtype=...)` → serialize to another format

Typical service flow:
1. Receive file path(s)
2. Parse with `ccread`
3. Return selected attributes (for example `scfenergies`, `atomcoords`, `moenergies`)
4. Optionally convert/export with `ccwrite`

### CLI fallback
If import-based execution is not suitable, subprocess the built-in commands:
- `ccget` (attribute extraction)
- `ccwrite` (format conversion)
- `ccframe` (table-style aggregation)
- `cda` (charge decomposition analysis)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `parse_file`
  - Input: `path`
  - Action: parse file with auto-detected parser
  - Output: normalized parsed-data handle + metadata

- `get_attributes`
  - Input: `path` or parsed-data handle, `attributes[]`
  - Action: return selected attributes only
  - Output: JSON-serializable subset (energies, coordinates, charges, etc.)

- `convert_output`
  - Input: `path` or parsed-data handle, `format` (`cjson|molden|xyz|wfx`), optional destination
  - Action: serialize parsed data
  - Output: converted content/path

- `run_method`
  - Input: parsed-data handle, `method` (`Bader|CDA|CM5|DDEC|Hirshfeld|MBO|Moments|Population|Volume|...`)
  - Action: run post-processing method if dependencies available
  - Output: method-specific results

- `list_supported_parsers`
  - Output: supported QC program parser names

- `health_check`
  - Output: service version, cclib version, optional dependency availability

---

## 5) Common Issues and Notes

- Parser coverage varies by program/version/output style. Keep fixtures for your lab’s templates.
- Large log files can be memory-heavy; prefer selective attribute retrieval when possible.
- Some analysis methods require extra scientific packages and may fail gracefully if missing.
- Bridge modules (ASE/OpenBabel/PySCF/etc.) should be exposed as optional services, gated by runtime checks.
- For robust production behavior:
  - validate input file existence and encoding
  - return structured errors (unsupported format, parse failure, missing dependency)
  - include parser name and confidence in responses

---

## 6) Reference Links and Documentation

- Repository: https://github.com/cclib/cclib
- Main package docs (project README and docs folder in repo)
- Key modules:
  - `cclib.io.ccio` (`ccopen`, `ccread`, `ccwrite`)
  - `cclib.parser.*` (program-specific parsers)
  - `cclib.method.*` (post-processing methods)
  - `cclib.scripts.*` (`ccget`, `ccwrite`, `ccframe`, `cda`)