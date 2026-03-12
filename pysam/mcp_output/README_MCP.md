# pysam MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps key `pysam` capabilities as MCP (Model Context Protocol) tools for bioinformatics workflows.  
It provides Python-dispatched access to common `samtools` and `bcftools` operations plus pileup helpers, enabling LLM/tooling systems to run sequence alignment and variant-processing tasks through a consistent service interface.

Main function groups:

- Alignment/BAM/CRAM operations (`samtools` wrappers)
- VCF/BCF operations (`bcftools` wrappers)
- Pileup data extraction helpers
- Runtime verbosity and error handling utilities

---

## 2) Installation Method

### Requirements

- Python >= 3.9
- Build/runtime ecosystem used by `pysam`:
  - `setuptools` (build-time)
  - `Cython` (typically needed for source builds)
  - Platform libraries commonly linked transitively: zlib/bz2/lzma/curl-related IO/compression stack
- Optional:
  - `pytest` for tests
  - `sphinx` for docs

### Install

Recommended (from PyPI):
- `pip install pysam`

For local development/service integration:
- `pip install -e .`
- `pip install -r requirements-dev.txt` (if you need tests/dev tooling)

If building from source in minimal containers, ensure compiler toolchain and compression/IO native libs are available.

---

## 3) Quick Start

Import and call wrapper modules directly in your MCP (Model Context Protocol) service handlers.

Example usage patterns:

- `import pysam`
- `pysam.samtools.view("-h", "input.bam")`
- `pysam.samtools.sort("-o", "sorted.bam", "input.bam")`
- `pysam.samtools.index("sorted.bam")`
- `pysam.bcftools.view("input.vcf.gz")`
- `pysam.bcftools.index("input.vcf.gz")`

Pileup helpers (from `pysam.Pileup`) expose convenience extractors such as:

- `get_query_sequences`
- `get_mapping_qualities`
- `get_query_qualities`
- `get_query_names`
- `get_num_aligned`
- `get_query_positions`

Typical MCP (Model Context Protocol) flow:

1. Receive tool call arguments (file path, region, options).
2. Map request to `pysam.samtools.*` or `pysam.bcftools.*`.
3. Return stdout/stderr/result payload to client.
4. Convert failures to structured tool errors (`SamtoolsError` where applicable).

---

## 4) Available Tools and Endpoints List

No standalone CLI entry points are defined in scanned metadata; expose these as MCP (Model Context Protocol) service endpoints/tools.

### Samtools-style service endpoints

- `view` — Read/convert/filter SAM/BAM/CRAM streams
- `sort` — Coordinate/name sort alignments
- `index` — Build BAM/CRAM index
- `flagstat` — Alignment summary stats
- `idxstats` — Per-reference mapped/unmapped counts
- `faidx` — FASTA index/query
- `mpileup` — Pileup generation
- `depth` — Per-position depth
- `merge` — Merge alignment files
- `fixmate` — Fix mate information
- `markdup` — Mark/remove duplicates
- `calmd` — Recalculate MD/NM tags
- `reheader` — Replace SAM/BAM header
- `stats` — Detailed alignment statistics
- `targetcut`, `phase`, `bedcov` — Additional samtools operations

### Bcftools-style service endpoints

- `index` — Index VCF/BCF
- `concat` — Concatenate variant files
- `merge` — Merge variant datasets
- `isec` — Set operations/intersections
- `stats` — Variant statistics
- `query` — Extract formatted fields
- `call` — Variant calling pipeline step
- `filter` — Apply expression filters
- `norm` — Normalize variants
- `annotate` — Add/update annotations
- `view` — Subset/transform VCF/BCF
- `reheader` — Replace headers/samples metadata
- `sort` — Sort records
- `consensus` — Build consensus sequence
- `service` — Run bcftools service interface function

### Utility endpoints (recommended)

- `set_verbosity` — Control underlying tool verbosity
- `get_verbosity` — Inspect current verbosity
- Error mapping via `SamtoolsError`

---

## 5) Common Issues and Notes

- Native dependency issues: most installation failures are due to missing compiler/system compression libraries.
- Environment parity: use the same container/base image for dev and production to avoid binary/linking drift.
- Large files/performance:
  - Prefer indexed random access (`.bai`, `.csi`, `.tbi`) over full scans.
  - Stream where possible; avoid loading full outputs into memory.
- Error handling:
  - Capture stderr from wrapped commands.
  - Return structured MCP (Model Context Protocol) errors with command + arguments context.
- Concurrency:
  - Be careful with temporary files and shared output paths.
  - Isolate per-request workspace in multi-tenant deployments.
- Testing:
  - Validate with representative BAM/CRAM/VCF sizes and edge-case headers/contigs.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pysam-developers/pysam
- Project docs (general): https://pysam.readthedocs.io/
- PyPI package: https://pypi.org/project/pysam/
- Source files of interest:
  - `pysam/samtools.py`
  - `pysam/bcftools.py`
  - `pysam/Pileup.py`
  - `pysam/utils.py`
  - `tests/` for practical usage patterns