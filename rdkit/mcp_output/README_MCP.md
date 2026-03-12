# RDKit MCP (Model Context Protocol) Service README

## 1) Project Introduction

This project provides an MCP (Model Context Protocol) service wrapper around RDKit for cheminformatics workflows.  
It is intended for LLM/tooling integrations that need molecule parsing, descriptor calculation, fingerprinting, similarity, substructure matching, and rendering.

Typical use cases:
- SMILES/InChI/mol block conversion and validation
- Molecular descriptors (2D/3D, QED, Lipinski, etc.)
- Fingerprint generation and similarity search
- Substructure and MCS matching
- Conformer/geometry operations
- Optional utilities for database workflows and feature extraction

---

## 2) Installation Method

### System requirements
- Python 3.10+ recommended
- RDKit installed with compiled C++ extensions
- `numpy` (required)
- Optional: `Pillow`, `pandas`, `scipy`, `matplotlib`, `IPython`, drawing backends (Cairo/Qt), InChI libs

### Recommended install (Conda)
- conda create -n rdkit-mcp -c conda-forge python=3.11 rdkit numpy
- conda activate rdkit-mcp

### Optional extras
- pip install pillow pandas scipy matplotlib ipython

### Verify installation
- python -c "from rdkit import Chem; print(Chem.MolFromSmiles('CCO') is not None)"

---

## 3) Quick Start

### Basic molecule operations
- Parse: `Chem.MolFromSmiles(...)`
- Canonicalize: `Chem.CanonSmiles(...)`
- Substructure: `mol.HasSubstructMatch(query)`
- Descriptors: `Descriptors.CalcMolDescriptors(mol)`
- Fingerprints + similarity: `DataStructs.FingerprintSimilarity(fp1, fp2)`
- Draw: `Draw.MolToImage(mol)`

### Typical MCP (Model Context Protocol) service flow
1. Client sends molecule input (SMILES/InChI/mol block).
2. Service validates and normalizes structure.
3. Service executes requested operation (descriptor/fingerprint/search/render/etc.).
4. Service returns structured JSON (result, warnings, errors).

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints/tools:

- `parse_molecule`
  - Input: SMILES/InChI/mol block
  - Output: normalized molecule metadata, canonical SMILES, validation status

- `compute_descriptors`
  - Output: selected descriptors (e.g., MolWt, LogP, TPSA, QED, counts)

- `generate_fingerprint`
  - Output: RDKit/Morgan/AtomPair/Torsion fingerprints (configurable params)

- `similarity`
  - Output: Tanimoto/Dice/Cosine similarity between two molecules/fingerprints

- `substructure_search`
  - Input: target + SMARTS query
  - Output: match boolean, atom/bond match indices

- `find_mcs`
  - Output: maximum common substructure (SMARTS, atom/bond counts)

- `enumerate_stereoisomers`
  - Output: stereoisomer set and count

- `enumerate_heterocycles`
  - Output: transformed heterocycle variants

- `standardize_molecule`
  - Output: cleaned/neutralized/tautomer-ordered form (MolStandardize)

- `draw_molecule`
  - Output: PNG/SVG payload or file reference

- `reaction_enumeration` (optional)
  - Output: products from reaction + building blocks

- `feature_finder_cli_bridge` (optional)
  - Bridges RDKit FeatFinderCLI-style functionality

- `db_create` / `db_search` (optional)
  - Wraps `Projects/DbCLI/CreateDb.py` and `SearchDb.py` workflows

---

## 5) Common Issues and Notes

- RDKit build/runtime mismatch:
  - Ensure the Python environment uses the same RDKit binary installation.
- Missing optional drawing deps:
  - Install Pillow/Cairo/Qt backends for image generation reliability.
- InChI failures:
  - Confirm InChI support is present in your RDKit build.
- Large batch performance:
  - Prefer batched calls; avoid per-molecule process startup.
  - Cache parsed molecules/fingerprints when possible.
- Threading:
  - Some operations are CPU-heavy; use process pools for throughput-critical services.
- Error handling:
  - Return clear parse/validation errors rather than failing silently.

---

## 6) Reference Links or Documentation

- RDKit repository: https://github.com/rdkit/rdkit
- Main README: https://github.com/rdkit/rdkit/blob/master/README.md
- RDKit Book / docs: https://github.com/rdkit/rdkit/tree/master/Docs/Book
- Installation guide: https://github.com/rdkit/rdkit/blob/master/Docs/Book/Install.md
- C++/Python getting started: https://github.com/rdkit/rdkit/blob/master/Docs/Book/GettingStartedInC%2B%2B.md
- Contrib utilities: https://github.com/rdkit/rdkit/tree/master/Contrib