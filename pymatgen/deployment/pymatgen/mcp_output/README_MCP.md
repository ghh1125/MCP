# pymatgen MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes high-value `pymatgen` capabilities through MCP (Model Context Protocol) endpoints for materials science workflows.

Main goals:
- Parse and manipulate crystal/molecular structures
- Compute composition and chemistry utilities
- Build/analyze phase diagrams and reactions
- Compare/deduplicate structures
- Parse/generate VASP input/output artifacts
- Optionally query external materials APIs (Materials Project, OPTIMADE)

Recommended usage style:
- **Primary:** direct Python imports (fast, deterministic)
- **Fallback:** wrap existing `pymatgen` CLI commands for selected tasks

---

## 2) Installation Method

### Prerequisites
- Python 3.10+ (recommended)
- `pip`

### Install core package
pip install pymatgen

### Optional extras (as needed by endpoints)
pip install mp-api ase plotly vtk seekpath phonopy h5py scikit-learn openbabel rdkit

### Typical required runtime libraries
- numpy, scipy, monty, ruamel.yaml, spglib, networkx, sympy, pandas
- matplotlib, tabulate, uncertainties, joblib, tqdm, requests

---

## 3) Quick Start

### A. Structure parsing/manipulation
- Input: CIF/POSCAR/string payload
- Output: normalized structure, composition, lattice/site summary

Example flow:
1. Create/load `Structure` or `Molecule`
2. Return formula, reduced composition, volume, site count

### B. Phase diagram analysis
- Input: list of entries (`PDEntry`-like payloads)
- Output: hull energies, stable/unstable phases, decomposition info

### C. Reaction balancing
- Input: reactant/product formulas (optionally energies)
- Output: balanced coefficients and reaction representation (`BalancedReaction` / `Reaction`)

### D. Structure matching
- Input: two structures
- Output: equivalent/not equivalent + matcher diagnostics (`StructureMatcher`)

### E. VASP I/O
- Input: INCAR/POSCAR/KPOINTS/POTCAR or vasprun.xml/OUTCAR content/path
- Output: parsed parameters/results in JSON-friendly format

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `structure.parse`
  - Parse structure text/files into canonical structure object summary.

- `structure.summarize`
  - Return lattice, species, formula, density, symmetry-ready metadata.

- `composition.analyze`
  - Formula parsing, reduced formula, element fractions, oxidation hints.

- `phase_diagram.build`
  - Build `PhaseDiagram` from entries and return stability map.

- `phase_diagram.decompose`
  - Decompose composition onto hull and report energy above hull.

- `reaction.balance`
  - Balance reactions using `BalancedReaction`/`Reaction`.

- `structure.match`
  - Compare two structures using `StructureMatcher` and tolerances.

- `vasp.inputs.parse`
  - Parse `Incar`, `Poscar`, `Kpoints`, `Potcar`.

- `vasp.outputs.parse`
  - Parse `Vasprun`, `Outcar` summaries (energies, bands, ionic steps, etc.).

- `external.matproj.query` (optional)
  - Materials Project lookups via `MPRester` (requires API key and `mp-api`).

- `external.optimade.query` (optional)
  - Federated OPTIMADE queries via `OptimadeRester`.

- `system.health`
  - Dependency/version checks and feature availability report.

---

## 5) Common Issues and Notes

- **Large import surface:** `pymatgen` is broad; lazy-load heavy modules in endpoints.
- **Optional dependency gaps:** some endpoints should be disabled gracefully if extras are missing.
- **API-backed tools:** external query endpoints need credentials/network; return clear auth errors.
- **Performance:** phase diagram and structure matching can be costly on large batches—support pagination/chunking.
- **Serialization:** convert complex pymatgen objects to JSON-safe payloads before MCP responses.
- **Reproducibility:** pin `pymatgen` + scientific stack versions in production.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/materialsproject/pymatgen
- Main docs index: https://pymatgen.org
- Installation guide (repo docs): `docs/installation.md`
- Usage guide (repo docs): `docs/usage.md`
- API-heavy module docs: `docs/pymatgen.md`
- Security policy: `SECURITY.md`