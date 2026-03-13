# pymatgen MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes core **pymatgen** capabilities through an MCP (Model Context Protocol) interface for materials science workflows.

Primary goals:
- Query materials data (Materials Project / OPTIMADE)
- Parse and convert simulation files (especially VASP)
- Run structured thermodynamic analyses (phase diagrams, Pourbaix diagrams)
- Use canonical materials objects (`Structure`, `Composition`, etc.) as service I/O

Best-fit use cases:
- AI agent tool-calling for materials retrieval and analysis
- Automated DFT post-processing pipelines
- Structure/data normalization across providers

---

## 2) Installation Method

### Prerequisites
- Python 3.10+
- Recommended: Linux/macOS, virtual environment

### Core dependencies
- numpy, scipy, monty, ruamel.yaml, spglib, networkx, pandas, matplotlib, sympy, requests, joblib, tabulate, tqdm, uncertainties

### Optional dependencies (feature-based)
- `mp-api` (Materials Project modern API)
- `ase`, `phonopy`, `seekpath`
- `h5py`, `pybtex`
- `openbabel`, `rdkit`
- `vtk`, `scikit-learn`

### Install steps
1. Create and activate a virtual environment  
2. Install pymatgen and required extras via pip (according to your target endpoints)  
3. If using Materials Project endpoints, set your API key in environment/config

---

## 3) Quick Start

### Typical service flow
1. Client sends crystal structure/composition or query parameters
2. Service converts input to pymatgen core objects
3. Service executes retrieval/parsing/analysis function
4. Service returns structured JSON-serializable result

### Example usage patterns
- **Materials query**: search by formula/system, return summarized entries
- **VASP parsing**: ingest `vasprun.xml` / `OUTCAR`, return energies, band info, metadata
- **Phase stability**: build `PhaseDiagram` from entries, return hull energy and stable phases
- **Aqueous stability**: build `PourbaixDiagram`, return stable domains/species

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `materials_project.search`
  - Wrapper around `pymatgen.ext.matproj.MPRester`
  - Query materials by formula, chemsys, IDs, properties

- `optimade.search`
  - Wrapper around `pymatgen.ext.optimade.OptimadeRester`
  - Federated provider search with normalized filters

- `structure.parse`
  - Parse structure text/file content into canonical `Structure`
  - Supports normalization and validation-friendly output

- `structure.convert`
  - Convert between common structure formats (CIF, POSCAR-like workflows, etc.)

- `vasp.parse_vasprun`
  - Parse VASP run outputs for energies, convergence, electronic metadata

- `vasp.parse_outcar`
  - Extract OUTCAR-derived quantities (magnetization, forces, run diagnostics)

- `thermo.phase_diagram.compute`
  - Use `PhaseDiagram`, `GrandPotentialPhaseDiagram`, `CompoundPhaseDiagram`
  - Return stable entries, decomposition, energy-above-hull metrics

- `electrochem.pourbaix.compute`
  - Use `PourbaixDiagram`/`PourbaixEntry`
  - Return stability regions and species information

- `core.validate_object`
  - Validate/roundtrip `Structure`, `Molecule`, `Composition`, `Element`, `Species`

---

## 5) Common Issues and Notes

- **API authentication**: Materials Project endpoints require a valid API key.
- **Optional dependency gaps**: some advanced endpoints fail unless extras are installed.
- **Large file parsing**: VASP outputs can be large; prefer streaming/size checks/timeouts.
- **Serialization**: use MSONable-compatible JSON for robust agent-to-service exchange.
- **Performance**: phase/Pourbaix analysis can be expensive on large entry sets; cache results where possible.
- **Environment reproducibility**: pin pymatgen + scientific stack versions in production.
- **Import strategy**: direct Python import is preferred; CLI fallback (`pmg`) is possible for constrained environments.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/materialsproject/pymatgen
- Official docs index: `docs/index.md` in repo
- Installation guide: `docs/installation.md`
- Usage guide: `docs/usage.md`
- API-heavy module docs: `docs/pymatgen.md`
- CLI entrypoint reference: `src/pymatgen/cli/pmg.py`
- Core external integrations:
  - `src/pymatgen/ext/matproj.py`
  - `src/pymatgen/ext/optimade.py`