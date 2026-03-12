# deepTools MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core **deepTools** genomics workflows so LLM clients or automation agents can run signal-processing and QC tasks in a consistent, tool-oriented interface.

It is designed for common NGS analysis tasks such as:

- BAM → coverage track generation
- Differential/comparative signal tracks
- Matrix computation around genomic regions
- Heatmap/profile plotting
- Multi-sample correlation and PCA QC
- GC bias estimation/correction
- Read filtering and alignment post-processing

Repository: https://github.com/deeptools/deepTools

---

## 2) Installation Method

### Requirements

- Python 3.8+ (recommended: 3.9/3.10)
- Core Python deps:
  - numpy
  - scipy
  - matplotlib
  - pysam
  - pyBigWig
- Optional (feature/environment dependent):
  - deeptoolsintervals
  - bx-python
  - Galaxy runtime components (only for Galaxy wrapper usage)

### Install with pip

- Install from PyPI:
  pip install deeptools

- Or install from source:
  git clone https://github.com/deeptools/deepTools.git  
  cd deepTools  
  pip install -e .

After install, verify:
bamCoverage --help

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) workflow

1. Create normalized tracks:
- Run `bamCoverage` for each BAM.
- Optionally run `bamCompare` for treatment/control ratio.

2. Build region-based matrix:
- Run `computeMatrix` using bigWig signal + BED/GTF regions.

3. Visualize:
- Run `plotHeatmap` and/or `plotProfile`.

4. Multi-sample QC:
- Run `multiBamSummary` or `multiBigwigSummary`.
- Then run `plotCorrelation` and `plotPCA`.

### Minimal command examples

bamCoverage -b sample.bam -o sample.bw --normalizeUsing CPM  
computeMatrix reference-point -S sample.bw -R genes.bed -o matrix.gz  
plotHeatmap -m matrix.gz -out heatmap.png  
plotProfile -m matrix.gz -out profile.png

---

## 4) Available Tools and Endpoints List

Each MCP (Model Context Protocol) endpoint maps to one deepTools command:

- **bamCoverage**: Generate normalized coverage tracks from BAM.
- **bamCompare**: Compare two BAMs (log2 ratio, subtraction, etc.).
- **computeMatrix**: Build signal matrices around regions/reference points.
- **computeMatrixOperations**: Filter/sort/subset/modify matrix files.
- **plotHeatmap**: Render heatmaps from computed matrices.
- **plotProfile**: Render aggregate profiles from matrices.
- **multiBamSummary**: Summarize multiple BAMs into count matrices.
- **multiBigwigSummary**: Summarize multiple bigWig files.
- **plotCorrelation**: Correlation heatmap/scatter from summary matrices.
- **plotPCA**: PCA visualization from summary outputs.
- **plotCoverage**: Coverage QC summary plot across samples.
- **plotFingerprint**: Enrichment/complexity QC fingerprint plot.
- **plotEnrichment**: Feature-centric enrichment plotting.
- **estimateReadFiltering**: Estimate effects of read filtering settings.
- **alignmentSieve**: Filter/transform alignments by flags/fragment criteria.
- **bigwigCompare**: Compare two bigWig tracks.
- **bigwigAverage**: Average multiple bigWig tracks.
- **computeGCBias**: Compute GC bias metrics.
- **correctGCBias**: Apply GC bias correction.
- **bamPEFragmentSize**: Estimate paired-end fragment size distributions.

---

## 5) Common Issues and Notes

- **Chromosome naming mismatch** (e.g., `chr1` vs `1`) is a frequent failure source.
- **Input indexing required**:
  - BAM files should be indexed (`.bai`).
  - bigWig inputs must be valid and readable.
- **Memory/CPU usage**:
  - `computeMatrix`, summaries, and plotting can be heavy on large cohorts.
  - Tune bin size, region count, and processor options for performance.
- **Headless environments**:
  - Ensure matplotlib backend works in server/CI contexts.
- **Dependency issues**:
  - `pysam`/`pyBigWig` build or binary compatibility may vary by OS.
  - Prefer clean virtual environments.
- **Output compatibility**:
  - Keep deepTools versions consistent across matrix generation and plotting steps.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/deeptools/deepTools
- Official docs: https://deeptools.readthedocs.io/
- Package metadata/config: `pyproject.toml` in repo root
- Changelog: `CHANGES.txt`
- Contributing guide: `.github/CONTRIBUTING.md`