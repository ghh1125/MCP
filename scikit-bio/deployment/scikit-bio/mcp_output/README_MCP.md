# scikit-bio MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service provides a developer-friendly interface to core **scikit-bio** capabilities for bioinformatics workflows.  
It focuses on:

- **Format-agnostic I/O** (`read`, `write`, `sniff`)
- **Sequence analysis** (`Sequence`, `DNA`, `RNA`, `Protein`)
- **Alignment** (pairwise alignment, `TabularMSA`)
- **Phylogenetics** (`TreeNode`, `nj`, `upgma`)
- **Diversity analysis** (alpha/beta diversity metrics)
- **Distance-based stats** (`permanova`, `anosim`, `mantel`, etc.)
- **Ordination** (`pcoa`, `pca`, `ca`, `cca`, `rda`)
- **Metadata handling** (`SampleMetadata`, interval metadata)

No dedicated CLI entry points were detected; this service is intended for API-driven usage.

---

## 2) Installation Method

### Requirements
Core dependencies:

- numpy
- scipy
- pandas

Common optional dependencies (feature-dependent):

- matplotlib
- h5py
- biom-format
- scikit-learn
- networkx
- python-dateutil

### Install commands

Install from PyPI:
pip install scikit-bio

Install with common optional scientific stack:
pip install scikit-bio matplotlib h5py scikit-learn networkx python-dateutil

---

## 3) Quick Start

Basic I/O:
from skbio import read, write

obj = read("input.fasta", format="fasta")
write(obj, format="fasta", into="output.fasta")

Sequence objects:
from skbio import DNA, RNA, Protein

dna = DNA("ACGTACGT")
rna = dna.transcribe()
protein = rna.translate()

Distance/statistics:
from skbio.stats.distance import DistanceMatrix, permanova

dm = DistanceMatrix([[0,1,2],[1,0,3],[2,3,0]], ids=["s1","s2","s3"])
# metadata_df should be a pandas DataFrame indexed by sample IDs
# result = permanova(dm, metadata_df, column="group")

Ordination:
from skbio.stats.ordination import pcoa
# ord_res = pcoa(dm)

Diversity:
from skbio.diversity import alpha_diversity, beta_diversity

# alpha = alpha_diversity("shannon", counts=[10,5,1], ids=["sample1"])
# beta = beta_diversity("braycurtis", counts_matrix, ids=sample_ids)

---

## 4) Available Tools and Endpoints List

For MCP (Model Context Protocol) service design, expose these practical endpoints:

- `io.read` → Unified file/object reader by format
- `io.write` → Unified writer to path/stream
- `io.sniff` → Format detection helper
- `sequence.create` → Build `Sequence`/`DNA`/`RNA`/`Protein`
- `alignment.pairwise.local` → Local pairwise alignment
- `alignment.pairwise.global` → Global pairwise alignment
- `alignment.msa.create` → Build/manage `TabularMSA`
- `tree.nj` → Neighbor-joining tree reconstruction
- `tree.upgma` → UPGMA tree reconstruction
- `distance.matrix.create` → Build `DistanceMatrix`/`DissimilarityMatrix`
- `stats.anosim` → ANOSIM permutation test
- `stats.permanova` → PERMANOVA permutation test
- `stats.permdisp` → Dispersion test
- `stats.mantel` / `stats.pwmantel` → Mantel tests
- `stats.bioenv` → Environmental variable selection by correlation
- `ordination.pcoa` / `ordination.pca` / `ordination.ca` / `ordination.cca` / `ordination.rda`
- `diversity.alpha` / `diversity.beta` / `diversity.partial_beta` / `diversity.block_beta`
- `metadata.load` → Load `SampleMetadata`
- `metadata.columns` → Access typed metadata columns
- `registry.list_metrics` → List available alpha/beta metrics

---

## 5) Common Issues and Notes

- **Format support is broad but explicit format hints are safer** when auto-detection is ambiguous.
- **Sample IDs must align** across distance matrices and metadata tables for statistical tests.
- **Permutation-based methods** (`permanova`, `anosim`, `mantel`) can be computationally expensive on large datasets.
- Some features require **optional dependencies**; missing libraries may raise import/runtime errors.
- This repository appears **API-first** (no standalone console services detected).
- Use isolated environments (venv/conda) for reproducible installs.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/biocore/scikit-bio
- Main package docs (project site): https://scikit.bio
- Source package root: `skbio/`
- Key modules:
  - `skbio.io`
  - `skbio.sequence`
  - `skbio.alignment`
  - `skbio.tree`
  - `skbio.diversity`
  - `skbio.stats.distance`
  - `skbio.stats.ordination`
  - `skbio.metadata`