# pybedtools MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps key `pybedtools` capabilities so developers can run genomic interval operations (intersection, merge, coverage, subtraction, annotation-style workflows) through service endpoints instead of shelling out manually.

`pybedtools` is a Python interface over the external BEDTools binaries, with additional helpers for genome registry lookup, parallel processing, and overlap matrix/venn-style utilities.

Main functions exposed by this service typically include:

- Core interval algebra via `BedTool`
- BED/GFF/VCF/BAM-aware operations through BEDTools backend
- Utility workflows (annotation, overlap matrix, intron/exon reads, venn/plot helpers)
- Optional contrib tools for visualization and intersection summaries

---

## 2) Installation Method

### Requirements

- Python >= 3.8
- `pybedtools`
- External `bedtools` binary installed and available on `PATH`
- Common Python deps: `numpy`, `pysam`

Optional (feature-dependent):

- `matplotlib` (plotting)
- `pyBigWig`
- `bx-python`
- `genomepy`

### Install

- Install BEDTools first (system package manager/conda)
- Then install Python package:

`pip install pybedtools`

If developing locally from source:

`pip install -e .`

---

## 3) Quick Start

### Python usage pattern behind the service

from pybedtools import BedTool

a = BedTool("a.bed")
b = BedTool("b.bed")

# Intersection
result = a.intersect(b, wa=True, wb=True)
print(result.head())

# Merge
merged = a.sort().merge()
print(len(merged))

# Subtract
sub = a.subtract(b)
print(sub.head())

### Typical MCP (Model Context Protocol) service flow

1. Send input file paths or interval content to a service endpoint.
2. Choose operation (`intersect`, `merge`, `subtract`, `coverage`, etc.).
3. Receive output path, interval rows, or summary stats.
4. Optionally chain operations (e.g., sort -> merge -> coverage).

---

## 4) Available Tools and Endpoints List

Below is a practical endpoint-style mapping for this MCP (Model Context Protocol) service.

- `bedtool.intersect`  
  Compute overlaps between interval sets; supports BEDTools-style flags.

- `bedtool.merge`  
  Merge overlapping/adjacent intervals, typically after sorting.

- `bedtool.subtract`  
  Remove intervals in B from A.

- `bedtool.coverage`  
  Compute coverage metrics of B over A intervals.

- `bedtool.closest`  
  Find nearest features between datasets.

- `bedtool.sort`  
  Sort intervals for deterministic downstream operations.

- `bedtool.shuffle`  
  Randomize interval locations (requires genome/chrom sizes).

- `bedtool.complement`  
  Return non-covered genome regions.

- `utils.parallel_apply`  
  Apply selected operations across many files in parallel.

- `contrib.intersection_matrix`  
  Build pairwise intersection summary matrix across multiple files.

- `script.annotate`  
  Annotation-oriented workflow service.

- `script.intersection_matrix`  
  CLI-equivalent matrix computation workflow service.

- `script.intron_exon_reads`  
  Intron/exon read counting workflow service.

- `script.peak_pie`  
  Peak annotation proportion reporting service.

- `script.venn_gchart` / `script.venn_mpl`  
  Venn overlap visualization services.

---

## 5) Common Issues and Notes

- BEDTools binary missing  
  Most failures come from `bedtools` not being installed or not on `PATH`.

- Input format issues  
  Ensure valid BED/GFF/VCF/BAM formatting and proper chromosome naming consistency.

- Sorting requirements  
  Some operations are faster/safer on sorted inputs (`sort` before `merge`, coverage-heavy workflows, etc.).

- Temp file usage  
  `pybedtools` is file-backed in many paths; monitor temp directory and clean up as needed.

- Performance considerations  
  Large interval sets can be I/O-heavy. Use batched workflows and `parallel_apply` where appropriate.

- Optional feature import errors  
  Plotting/bigwig/contrib functions may require extra optional dependencies.

- Environment reproducibility  
  Pin BEDTools + pybedtools versions in production to avoid command-behavior drift.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/daler/pybedtools
- Python package docs (source/docs in repo): `docs/source/`
- Key modules:
  - `pybedtools/bedtool.py`
  - `pybedtools/helpers.py`
  - `pybedtools/parallel.py`
  - `pybedtools/contrib/intersection_matrix.py`
- BEDTools project (backend dependency): https://bedtools.readthedocs.io/