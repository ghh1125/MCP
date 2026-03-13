# Biopython MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core Biopython APIs as MCP (Model Context Protocol) tools for sequence, alignment, structure, phylogeny, search-result parsing, and NCBI Entrez retrieval workflows.

Primary goals:
- Provide stable, developer-friendly bioinformatics operations via MCP (Model Context Protocol)
- Expose high-value Biopython modules (`SeqIO`, `AlignIO`, `Align`, `PDB`, `Phylo`, `SearchIO`, `Entrez`)
- Enable format conversion, parsing, indexing, and basic analysis in a tool-callable interface

---

## 2) Installation Method

### Requirements
- Python 3.x
- `biopython`
- `numpy` (required by Biopython)

Optional (feature-dependent):
- `reportlab` (graphics/genome diagrams)
- `matplotlib` (phylo plotting)
- `networkx` or `igraph` (some phylo integrations)
- `mmtf-python` (MMTF support)
- DB drivers for BioSQL: `mysqlclient` / `mysql-connector-python` / `psycopg2` / `sqlite3`
- External binaries for some modules: DSSP, NACCESS, PAML, BLAST tools

### Install
pip install biopython numpy

Optional extras (as needed):
pip install reportlab matplotlib networkx mmtf-python

---

## 3) Quick Start

### Minimal usage flow
1. Start your MCP (Model Context Protocol) host runtime
2. Register this Biopython service
3. Call tools such as sequence parse/read/write or alignment/structure parsers

### Typical tool calls (conceptual)
- Parse FASTA/GenBank records using `SeqIO.parse` / `SeqIO.read`
- Convert sequence formats using `SeqIO.convert`
- Parse alignments using `AlignIO.parse` or modern `Bio.Align.parse`
- Load substitution matrices via `Bio.Align.substitution_matrices.load`
- Parse PDB/mmCIF structures with `PDBParser` / `MMCIFParser`
- Read/convert phylogenetic trees via `Phylo.read` / `Phylo.convert`
- Parse BLAST/HMMER outputs via `SearchIO.parse`
- Query NCBI with `Entrez.esearch` + `Entrez.efetch`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) endpoints for this service:

- `seqio_parse`
  - Parse multi-record sequence files (FASTA/GenBank/EMBL/FASTQ/etc.)
- `seqio_read`
  - Read exactly one sequence record
- `seqio_write`
  - Write sequence records to target format
- `seqio_convert`
  - Convert sequence files between supported formats
- `seqio_index` / `seqio_index_db`
  - Build lightweight/random-access sequence indexes

- `alignio_parse` / `alignio_read` / `alignio_write` / `alignio_convert`
  - Multiple sequence alignment I/O and conversion

- `align_parse` / `align_read` / `align_write`
  - Modern `Bio.Align` alignment APIs
- `pairwise_align`
  - Pairwise alignment via `PairwiseAligner`
- `load_substitution_matrix`
  - Load scoring matrices (e.g., BLOSUM/PAM)

- `pdb_parse`
  - Parse PDB files
- `mmcif_parse`
  - Parse mmCIF files
- `pdb_write`
  - Export structures
- `structure_superimpose` / `neighbor_search`
  - Structural comparison and proximity queries

- `phylo_read` / `phylo_parse` / `phylo_write` / `phylo_convert`
  - Phylogenetic tree I/O workflows

- `searchio_parse` / `searchio_read` / `searchio_index` / `searchio_convert`
  - Search tool output parsing (BLAST/HMMER/Infernal/Exonerate)

- `entrez_esearch` / `entrez_efetch` / `entrez_esummary` / `entrez_elink`
  - NCBI E-utilities access (network dependent)

---

## 5) Common Issues and Notes

- No first-class package CLI entry points are defined; Biopython is primarily a library.
- Some capabilities require optional dependencies or external binaries.
- Entrez usage requires internet and proper NCBI etiquette (`Entrez.email`, rate-limit awareness, API key if needed).
- Large files (BAM-like, big alignments, massive GenBank) should use streaming/indexing to avoid memory pressure.
- Format strictness varies; malformed biological files may parse partially or fail.
- BioSQL features need database-specific drivers and schema setup.
- Use pinned versions in production for reproducibility.

---

## 6) Reference Links / Documentation

- Biopython repository: https://github.com/biopython/biopython
- Biopython docs: https://biopython.org/wiki/Documentation
- API docs: https://biopython.org/docs/latest/api/
- Tutorial & Cookbook: https://biopython.org/DIST/docs/tutorial/Tutorial.html
- NCBI Entrez E-utilities: https://www.ncbi.nlm.nih.gov/books/NBK25501/