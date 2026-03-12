# PlantCV MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core PlantCV capabilities for plant image analysis workflows.  
It is designed for developers who want to expose PlantCV functions as callable services for automation, pipelines, or agent-based analysis.

Main capabilities include:

- Image preprocessing (crop, blur, masking, transforms)
- Segmentation and thresholding
- ROI construction and filtering
- Trait extraction and measurement (size, color, grayscale, spectral, thermal, fluorescence)
- Batch/parallel workflow execution
- Utility and ML helpers (k-means, naive Bayes tooling)

Primary Python API surface: `plantcv.plantcv` (import-first strategy, low intrusiveness).

---

## 2) Installation Method

### Prerequisites

- Python 3.9+ recommended
- Native dependencies required by OpenCV/scikit-image stack

### Core dependencies

- numpy
- opencv-python
- scikit-image
- scipy
- matplotlib
- pandas

Optional (feature-dependent): xarray, dask, rasterio, h5py, imageio, altair.

### Install commands

- From PyPI:
  - `pip install plantcv`
- From source repository:
  - `pip install .`
- Conda-style environment is available via `environment.yml` in the repository.

---

## 3) Quick Start

### Minimal service usage flow

1. Read image  
2. Apply segmentation/threshold  
3. Define ROI (if needed)  
4. Run analysis (e.g., size/color)  
5. Collect outputs/measurements

### Example function flow (service-side mapping)

- `readimage` → load image
- `threshold.binary` / `threshold.otsu` → mask generation
- `roi.rectangle` / `roi.circle` → region selection
- `analyze.size.analyze_object` → trait extraction
- `Outputs` → structured result export

For CLI-oriented workflows, service wrappers can also call:

- `plantcv.parallel.cli:main`
- `plantcv.learn.cli:main`
- `plantcv.utils.cli:main`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `image.read`  
  Load image data and metadata (`readimage`).

- `image.preprocess`  
  Common preprocessing operations (masking, blur, invert, arithmetic, morphology).

- `threshold.apply`  
  Thresholding methods: binary, custom_range, gaussian, mean, otsu, saturation, texture, triangle.

- `roi.create`  
  ROI generators: rectangle, circle, ellipse, custom, multi, auto_grid, auto_wells.

- `analyze.size`  
  Object size/shape and related measurements (`analyze_object`, bounds, NIR intensity).

- `analyze.color_grayscale`  
  Color and grayscale trait extraction.

- `analyze.spectral_thermal_fluorescence`  
  Spectral index/reflectance, thermal, NPQ/YII analysis.

- `workflow.parallel`  
  Build/inspect/run/process parallel jobs.

- `ml.tools`  
  k-means and naive Bayes training/classification helpers.

- `utils.convert_export`  
  Dataset/helper conversions and output formatting.

---

## 5) Common Issues and Notes

- OpenCV install issues: use a clean virtual environment and ensure compatible Python wheels.
- Large image datasets: prefer parallel workflow endpoints to reduce wall time.
- Memory pressure: hyperspectral and batch operations can be heavy; process in chunks.
- Optional dependency errors: only install extras required by your selected endpoints.
- Consistent outputs: standardize ROI and threshold parameters across experiments for reproducibility.
- Testing coverage is extensive in `tests/`; use it as reference for expected behavior and edge cases.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/danforthcenter/plantcv
- Main docs index: `docs/index.md`
- Installation guide: `docs/installation.md`
- Parallel workflows: `docs/pipeline_parallel.md` and `docs/parallel_config.md`
- Outputs and measurements: `docs/outputs.md` and `docs/output_measurements.md`
- Spectral workflows: `docs/spectral_index.md`
- Contribution guide: `docs/CONTRIBUTING.md`