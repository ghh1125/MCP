# pymatgen MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps key `pymatgen` capabilities into MCP (Model Context Protocol) tools for materials-science workflows.  
It is designed for LLM/tooling integration where users need structured operations such as:

- Crystal/molecule parsing and conversion
- VASP input/output parsing
- Phase diagram and reaction analysis
- Local environment analysis (coordination/nearest neighbors)
- Remote data access (Materials Project, OPTIMADE)

Target users: developers building scientific assistants, automation pipelines, or agentic research tools.

---

## 2) Installation Method

### Requirements

Core Python dependencies commonly needed by `pymatgen`:

- numpy, scipy, monty, ruamel.yaml
- spglib, networkx
- matplotlib, pandas, sympy
- requests, tqdm

Optional (feature-specific): `mp-api`, `ase`, `seekpath`, `phonopy`, `h5py`, `plotly`, `vtk`, `openbabel`, `rdkit`.

### Install

1. Create and activate a virtual environment.
2. Install pymatgen:
   pip install pymatgen
3. (Optional) Install extra integrations as needed:
   pip install mp-api ase seekpath phonopy h5py plotly

If your MCP (Model Context Protocol) host runs the service in isolation, ensure the same environment is used by both the host and service process.

---

## 3) Quick Start

Typical MCP (Model Context Protocol) usage pattern:

1. Start the pymatgen MCP (Model Context Protocol) service.
2. Call a tool endpoint with JSON-like arguments.
3. Receive structured results (dict/list), then pass to downstream reasoning or plotting tools.

Example workflows:

- Parse a VASP `vasprun.xml` and extract final energy/structure.
- Build a `PhaseDiagram` from entries and query decomposition/energy above hull.
- Analyze local coordination around selected atomic sites with `CrystalNN`.
- Balance a chemical reaction using reaction calculator utilities.
- Query Materials Project with `MPRester` (requires API key).

---

## 4) Available Tools and Endpoints List

Suggested core endpoints for this MCP (Model Context Protocol) service:

- `structure.parse`
  - Load structures/molecules from common formats (CIF, POSCAR, etc.).
- `structure.convert`
  - Convert structure representations and export to target format.
- `vasp.inputs.read`
  - Parse POSCAR/INCAR/KPOINTS/POTCAR metadata.
- `vasp.outputs.read`
  - Parse Vasprun/OUTCAR/OSZICAR/XDATCAR and extract key results.
- `analysis.phase_diagram`
  - Construct/query `PhaseDiagram`, `GrandPotentialPhaseDiagram`, etc.
- `analysis.reaction.balance`
  - Balance reactions and compute reaction energetics where data is available.
- `analysis.local_env`
  - Coordination analysis with `CrystalNN`, `VoronoiNN`, `MinimumDistanceNN`.
- `ext.materials_project.query`
  - Query MP data via `MPRester` (network/API-key dependent).
- `ext.optimade.query`
  - Federated OPTIMADE queries via `OptimadeRester`.

---

## 5) Common Issues and Notes

- Version compatibility:
  - Keep Python and `pymatgen` versions pinned in production.
- Heavy parsing:
  - Large VASP XML/output files can be memory-intensive; stream/process in batches where possible.
- Optional dependency errors:
  - Install only required extras for enabled endpoints to reduce conflicts.
- API/network failures:
  - For MP/OPTIMADE endpoints, handle retries, timeouts, and missing credentials.
- Scientific reproducibility:
  - Record `pymatgen` version, input files, and endpoint parameters in logs/artifacts.
- Runtime performance:
  - Neighbor finding and some thermodynamic analyses can be CPU-heavy for large structures.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/materialsproject/pymatgen
- Official docs index: https://pymatgen.org
- Usage docs (repo): `docs/usage.md`
- Installation docs (repo): `docs/installation.md`
- CLI reference entry: `src/pymatgen/cli/pmg.py`
- Security policy: `SECURITY.md`