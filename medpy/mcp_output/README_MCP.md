# MedPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core capabilities from **[medpy](https://github.com/loli/medpy)** for medical image processing workflows.

It is designed for developers who need programmatic access to:

- Medical image I/O (load/save + metadata)
- Filtering and preprocessing (resampling, smoothing, morphology)
- Feature extraction (intensity, histogram, texture)
- Segmentation utilities (watershed, graph-cut workflows)
- Evaluation metrics (Dice, Hausdorff, ASD/ASSD, etc.)

Repository analyzed: `loli/medpy` (Python package with CLI tools and test coverage).

---

## 2) Installation Method

### Requirements

- Python 3.8+ recommended
- Required:
  - `numpy`
  - `scipy`
- Optional (depending on formats/features used):
  - `SimpleITK`
  - `pydicom`
  - `nibabel`
  - `networkx`
  - `maxflow` / `pymaxflow`

### Install commands

- Install MedPy:
  - `pip install medpy`
- Or install from source:
  - `git clone https://github.com/loli/medpy.git`
  - `cd medpy`
  - `pip install .`

If graph-cut functionality is required, ensure a compatible maxflow backend is installed.

---

## 3) Quick Start

### Python API style usage

- Load image:
  - `medpy.io.load(path)` → `(array, header)`
- Save image:
  - `medpy.io.save(array, output_path, hdr=header)`
- Resample image:
  - `medpy.filter.image.resample(img, hdr, target_spacing, bspline_order=3, mode='nearest')`
- Metrics:
  - `medpy.metric.binary.dc(result, reference)` (Dice)
  - `medpy.metric.binary.hd95(result, reference, voxelspacing=..., connectivity=1)`

### CLI-style workflow examples (service-wrapped)

- Inspect metadata: `medpy_info`
- Convert image format: `medpy_convert`
- Compare volumes: `medpy_diff`
- Resample volume: `medpy_resample`
- Anisotropic diffusion: `medpy_anisotropic_diffusion`
- Watershed segmentation: `medpy_watershed`
- Graph-cut segmentation: `medpy_graphcut_voxel`, `medpy_graphcut_label`

In MCP (Model Context Protocol) deployments, these are typically exposed as service endpoints/tools rather than raw shell commands.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `image_info`
  - Backed by: `medpy_info`
  - Returns shape, spacing, datatype, header metadata summary.

- `image_convert`
  - Backed by: `medpy_convert`
  - Converts between supported medical image formats.

- `image_diff`
  - Backed by: `medpy_diff`
  - Computes/report differences between two images.

- `image_resample`
  - Backed by: `medpy_resample` / `medpy.filter.image.resample`
  - Resamples to target voxel spacing or geometry.

- `anisotropic_diffusion`
  - Backed by: `medpy_anisotropic_diffusion` / `medpy.filter.smoothing.anisotropic_diffusion`
  - Noise reduction with edge-preserving smoothing.

- `watershed_segment`
  - Backed by: `medpy_watershed`
  - Watershed-based segmentation pipeline.

- `graphcut_voxel_segment`
  - Backed by: `medpy_graphcut_voxel`
  - Voxel-level graph-cut segmentation.

- `graphcut_label_segment`
  - Backed by: `medpy_graphcut_label`
  - Label-based graph-cut segmentation.

- `segmentation_metrics`
  - Backed by: `medpy.metric.binary`
  - Dice, Jaccard, Hausdorff, ASD/ASSD, sensitivity/specificity.

- `feature_extraction`
  - Backed by: `medpy.features.intensity|histogram|texture`
  - Computes handcrafted radiomics-style feature vectors.

---

## 5) Common Issues and Notes

- **Optional dependency gaps**  
  Some image formats require `SimpleITK`, `pydicom`, or `nibabel`. Missing backends can cause load/save errors.

- **Graph-cut setup**  
  Graph-cut tools may fail without `maxflow/pymaxflow` and compatible compiled components.

- **Metadata consistency**  
  When resampling/saving, preserve and validate header spacing/origin metadata (`medpy.io.header` helpers).

- **Large volume performance**  
  3D/4D processing can be memory-intensive. Prefer chunk/patch workflows where possible.

- **Input assumptions**  
  Many metric functions assume binary masks and aligned geometry. Always verify shape, spacing, and orientation before evaluation.

- **Import feasibility**  
  Analysis indicates good integration feasibility (~0.84) with low intrusiveness and medium complexity.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/loli/medpy
- Package docs/readme (in repo): `README.md`, `README_PYPI.md`
- Tests for usage patterns: `tests/`
- CLI scripts: `bin/`
- Core modules:
  - `medpy.io`
  - `medpy.filter`
  - `medpy.features`
  - `medpy.metric`
  - `medpy.graphcut`