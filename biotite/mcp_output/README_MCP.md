# biotite MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core **Biotite** capabilities for sequence/structure bioinformatics workflows.  
It is designed for developer use in LLM/tooling pipelines and provides practical operations such as:

- Sequence alignment (global/local/banded)
- FASTA read/write utilities
- Protein structure I/O (PDB, mmCIF/BinaryCIF)
- RCSB/UniProt query + structure download
- Structure superimposition and RMSD-style comparison

Repository: https://github.com/biotite-dev/biotite

---

## 2) Installation Method

### Requirements
- Python 3.10+ (recommended)
- Required: `numpy`
- Common optional dependencies (feature-dependent): `scipy`, `matplotlib`, `requests`, `networkx`, `msgpack`, `biotraj`, `rdkit`, `openmm`, `pymol`

### Install
- Core:
  `pip install biotite`
- With common extras manually:
  `pip install biotite requests scipy matplotlib networkx msgpack`

If you are developing the MCP (Model Context Protocol) service itself, install from source in editable mode:
`pip install -e .`

---

## 3) Quick Start

### Sequence alignment
- Use `biotite.sequence.align`:
  - `align_optimal()`
  - `align_local_ungapped()`
  - `align_local_gapped()`
  - `align_banded()`
- Returned `Alignment` objects contain aligned traces/scores for downstream reporting.

### FASTA I/O
- Use `biotite.sequence.io.fasta.file.FastaFile`
  - `get_sequences()` to parse records
  - `set_sequences()` to write records

### Structure I/O
- PDB:
  - `biotite.structure.io.pdb.file.PDBFile`
  - `get_structure()`, `set_structure()`, `list_assemblies()`, `get_assembly()`
- mmCIF/BinaryCIF:
  - `biotite.structure.io.pdbx.convert`
  - `get_structure()`, `set_structure()`, `get_component()`, `set_component()`

### Remote retrieval
- RCSB search/query:
  - `biotite.database.rcsb.query.search()`, `count()`, `sort()`
- RCSB fetch:
  - `biotite.database.rcsb.download.fetch()`
- UniProt query:
  - `biotite.database.uniprot.query.search()` with query composition classes

### Structure comparison
- `biotite.structure.superimpose`
  - `superimpose()`, `superimpose_homologs()`, `rmsd()`, `rmspd()`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoint surface:

- `sequence.align.optimal`  
  Global/pairwise optimal alignment.

- `sequence.align.local_ungapped`  
  Fast local ungapped alignment.

- `sequence.align.local_gapped`  
  Local gapped alignment for sensitive matching.

- `sequence.align.banded`  
  Constrained alignment for large similar sequences.

- `sequence.fasta.read`  
  Parse FASTA records to structured sequence objects.

- `sequence.fasta.write`  
  Serialize sequence objects to FASTA.

- `structure.pdb.read`  
  Load PDB into atom arrays/structure objects.

- `structure.pdb.write`  
  Export structures to PDB.

- `structure.pdb.assemblies`  
  List/extract biological assemblies.

- `structure.pdbx.read`  
  Read mmCIF/BinaryCIF structures.

- `structure.pdbx.write`  
  Write mmCIF/BinaryCIF structures.

- `database.rcsb.search`  
  Search RCSB PDB by query schema.

- `database.rcsb.count`  
  Count hits for an RCSB query.

- `database.rcsb.fetch`  
  Download structures by ID/format.

- `database.uniprot.search`  
  Search UniProt and return matching entries.

- `structure.superimpose`  
  Superimpose structures and return transform + score metrics.

- `structure.rmsd`  
  Compute RMSD/RMSPD between structures/aligned atoms.

---

## 5) Common Issues and Notes

- Some capabilities require optional libraries; install only what your service endpoints use.
- Network-facing endpoints (RCSB/UniProt) require stable internet and may need retry/throttling logic.
- Large structure files (especially mmCIF/BinaryCIF) can be memory-heavy—streaming/chunking is recommended in service handlers.
- PyMOL/OpenMM/RDKit integrations are optional and environment-sensitive.
- Keep endpoint contracts strict (input validation for sequence alphabets, residue/chain selection, file formats).
- Add caching for repeated remote queries to improve latency/cost.

---

## 6) Reference Links / Documentation

- Biotite repository: https://github.com/biotite-dev/biotite
- Project docs/examples are in the repository `doc/` directory
- Key source paths:
  - `src/biotite/sequence/align/`
  - `src/biotite/sequence/io/fasta/`
  - `src/biotite/structure/io/pdb/`
  - `src/biotite/structure/io/pdbx/`
  - `src/biotite/database/rcsb/`
  - `src/biotite/database/uniprot/`
  - `src/biotite/structure/superimpose.py`