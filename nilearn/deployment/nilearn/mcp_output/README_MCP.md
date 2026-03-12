# Nilearn MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository is the source code of **Nilearn**, a Python library for neuroimaging (fMRI/MRI) analysis built on NumPy, SciPy, scikit-learn, nibabel, and matplotlib.

If you expose Nilearn through an MCP (Model Context Protocol) service, the service can provide practical analysis capabilities such as:

- Dataset fetching and loading
- Image preprocessing and masking
- Statistical modeling (GLM, first/second level)
- Decoding and machine-learning workflows
- Connectivity and region-based analysis
- Static/interactive plotting and reporting

Core Nilearn modules you will likely wrap as MCP (Model Context Protocol) services:
- `nilearn.datasets`
- `nilearn.image`
- `nilearn.maskers`
- `nilearn.glm`
- `nilearn.decoding`
- `nilearn.connectome`
- `nilearn.plotting`
- `nilearn.reporting`
- `nilearn.surface`, `nilearn.regions`, `nilearn.signal`

---

## 2) Installation Method

### Requirements
- Python (use a modern 3.x version compatible with the project `pyproject.toml`)
- Scientific stack (installed automatically with pip): NumPy, SciPy, scikit-learn, nibabel, pandas, matplotlib, etc.

### Install from PyPI
pip install nilearn

### Install latest development version
pip install git+https://github.com/nilearn/nilearn.git

### For MCP (Model Context Protocol) service development
Also install your MCP server framework/runtime, then import Nilearn in your service handlers.

---

## 3) Quick Start

Typical flow for an MCP (Model Context Protocol) service:

1. Receive request (dataset ID, file paths, analysis params)
2. Call Nilearn APIs
3. Return structured output (paths, metrics, figures, tables)

Minimal usage example (inside a service handler):
- Load or fetch data via `nilearn.datasets`
- Build masker (`NiftiMasker` / `NiftiLabelsMasker`)
- Fit/transform signals
- Run model or decoding
- Return summary statistics and artifact locations

Common callable APIs to expose:
- `nilearn.datasets.fetch_*`
- `nilearn.image.load_img`, `clean_img`, `smooth_img`, `resample_to_img`
- `nilearn.maskers.NiftiMasker`, `NiftiLabelsMasker`, `NiftiMapsMasker`
- `nilearn.glm.first_level.FirstLevelModel`
- `nilearn.glm.second_level.SecondLevelModel`
- `nilearn.decoding.Decoder`, `SearchLight`
- `nilearn.connectome.ConnectivityMeasure`
- `nilearn.plotting.plot_stat_map`, `plot_connectome`
- `nilearn.reporting.make_glm_report` (via reporting utilities)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (suggested design):

- `datasets.fetch`
  - Download/load standard datasets and return local paths + metadata.

- `image.preprocess`
  - Perform smoothing, resampling, masking, cleaning, and basic transforms.

- `maskers.fit_transform`
  - Fit a masker and extract time series from NIfTI/surface data.

- `glm.first_level.fit`
  - Fit single-subject first-level GLM; return contrasts/maps.

- `glm.second_level.fit`
  - Fit group-level model; return statistical maps and thresholded outputs.

- `decoding.run`
  - Run classifier/regressor decoding pipelines; return scores and model metadata.

- `connectome.compute`
  - Build connectivity matrices from extracted time series.

- `plot.generate`
  - Create brain/stat/connectome figures; return file paths or serialized outputs.

- `report.generate`
  - Produce GLM/analysis HTML summaries for downstream review.

---

## 5) Common Issues and Notes

- **Large downloads**: dataset fetchers can be slow; configure cache/data directories.
- **Memory usage**: 4D images and voxelwise models can be heavy; use maskers and chunked workflows.
- **Headless environments**: for plotting on servers, configure non-interactive matplotlib backend.
- **Version compatibility**: pin Nilearn + scikit-learn + nibabel in production.
- **No built-in CLI detected**: this repo is primarily a Python library, so MCP (Model Context Protocol) integration should call Python APIs directly.
- **Testing**: repository includes extensive tests and tox/CI configs; reuse for service validation.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/nilearn/nilearn
- Official docs: https://nilearn.github.io/
- User guide: https://nilearn.github.io/stable/user_guide.html
- API reference: https://nilearn.github.io/stable/modules/reference.html
- Examples gallery: https://nilearn.github.io/stable/auto_examples/index.html
- Development/packaging config: `pyproject.toml` in repository root