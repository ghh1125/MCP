# Biopython MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core Biopython capabilities into developer-friendly tools for bioinformatics workflows.  
It focuses on:

- Biological sequence operations (`Bio.Seq`)
- Sequence file I/O and format conversion (`Bio.SeqIO`)
- Alignment parsing/writing and pairwise alignment (`Bio.Align`, `Bio.AlignIO`)
- Search result parsing (BLAST/HMMER/Infernal via `Bio.SearchIO`, `Bio.Blast`)
- Structure parsing and processing (`Bio.PDB`)
- Phylogenetic tree I/O and visualization helpers (`Bio.Phylo`)
- NCBI Entrez data retrieval (`Bio.Entrez`)

Best suited for automation, data ingestion pipelines, and LLM-driven bioinformatics tasks.

---

## 2) Installation Method

### Requirements
- Python 3.x
- `biopython`
- `numpy` (core dependency)

Optional (feature-specific): `matplotlib`, `networkx`, `reportlab`, `lxml`, `rdflib`, `Pillow`, `mmtf-python`, SQL drivers (`mysqlclient`, `mysql-connector-python`, `psycopg2`).

### Install
- `pip install biopython numpy`
- Optional extras as needed, e.g.:
  - `pip install matplotlib networkx`
  - `pip install lxml rdflib Pillow`
  - `pip install mmtf-python`

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow
1. Connect MCP (Model Context Protocol) client to this service.
2. Call a tool endpoint (e.g., sequence parse, translate, alignment parse).
3. Receive normalized JSON-like results for downstream orchestration.

### Example usage patterns
- Parse FASTA/GenBank records with `SeqIO.parse`/`SeqIO.read`
- Translate DNA/RNA using `Bio.Seq.translate`
- Convert formats with `SeqIO.convert` or `AlignIO.convert`
- Parse BLAST/HMMER output with `SearchIO.parse`
- Read structures using `PDBParser` or `MMCIFParser`
- Fetch NCBI data with `Entrez.esearch` + `Entrez.efetch`

---

## 4) Available Tools and Endpoints List

Recommended endpoint set for this MCP (Model Context Protocol) service:

- `seq.transform`  
  Transcribe, back-transcribe, translate, reverse complement (DNA/RNA).

- `seqio.parse`  
  Parse sequence files (FASTA, GenBank, EMBL, etc.) into records.

- `seqio.read`  
  Read a single sequence record from a file/string source.

- `seqio.write`  
  Write records to output format.

- `seqio.convert`  
  Convert between sequence formats.

- `align.parse` / `align.read` / `align.write`  
  Work with modern alignment formats and `Alignment` objects.

- `align.pairwise`  
  Pairwise alignment using `PairwiseAligner`.

- `alignio.parse` / `alignio.convert`  
  Legacy/compatible alignment I/O paths.

- `searchio.parse` / `searchio.read` / `searchio.write`  
  Parse and export search results (BLAST, HMMER, Infernal, Exonerate, etc.).

- `pdb.parse`  
  Parse PDB/mmCIF structures.

- `pdb.analyze`  
  Neighbor search, superimposition, basic structure-level operations.

- `phylo.parse` / `phylo.read` / `phylo.write` / `phylo.convert`  
  Tree I/O and format transformations.

- `entrez.esearch` / `entrez.efetch` / `entrez.esummary`  
  NCBI Entrez retrieval and parsing.

---

## 5) Common Issues and Notes

- Always set `Entrez.email` (and API key if available) to avoid NCBI throttling.
- Large files (BAM-like outputs, big alignments, huge FASTA) should be streamed/chunked.
- Format auto-detection is limited; prefer explicit format names.
- Some modules require optional dependencies (graphics, XML, DB backends).
- Biopython includes legacy and modern APIs (`AlignIO` vs `Align`); pick one style consistently.
- Structure and search parsing can be CPU/memory heavy on very large datasets.
- Internet-dependent tools (Entrez, remote resources) should have retries/timeouts.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/biopython/biopython
- Biopython Documentation: https://biopython.org/wiki/Documentation
- API Docs (latest): https://biopython.org/docs/latest/api/
- Tutorial & Cookbook: https://biopython.org/DIST/docs/tutorial/Tutorial.html
- NCBI Entrez Usage Guidelines: https://www.ncbi.nlm.nih.gov/books/NBK25497/

If you want, I can also provide a production-ready `tools` schema (names, params, and response models) for direct MCP (Model Context Protocol) server implementation.