# MNE-Python MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core **MNE-Python** capabilities for EEG/MEG workflows in an MCP (Model Context Protocol)-friendly interface.

Primary goals:
- Load raw neurophysiology data (FIF, EDF, BDF, BrainVision).
- Perform event handling and channel picking.
- Run common preprocessing (EOG/ECG detection, ICA-related preparation).
- Compute PSD and time-frequency features.
- Optionally render diagnostic visualizations (when GUI/backends are available).

Recommended integration path:
- **Primary:** in-process Python imports from `mne` modules.
- **Fallback:** call the `mne` CLI for heavier or isolated execution contexts.

---

## 2) Installation Method

### Requirements
Core dependencies:
- `numpy`
- `scipy`
- `matplotlib`
- `packaging`
- `pooch`
- `tqdm`

Common optional dependencies (feature-dependent):
- `scikit-learn`, `pandas`, `h5py`, `nibabel`
- `pyvista`, `vtk`, `mne-qt-browser`
- `numba`

### Install
- Install MNE-Python and common scientific stack via pip:
  - `pip install mne`
- For broader functionality:
  - `pip install mne[full]` (if supported by your environment/version)
- If your service uses project-local dependency files, prefer:
  - `pyproject.toml` / `environment.yml` in your deployment workflow.

---

## 3) Quick Start

### Minimal service flow (Python-side)
1. Read raw data:
   - `mne.io.read_raw_fif(...)` / `read_raw_edf(...)` / `read_raw_bdf(...)` / `read_raw_brainvision(...)`
2. Extract events:
   - `mne.find_events(raw)` or `mne.read_events(path)`
3. Pick channels:
   - `mne.pick_types(raw.info, meg=True, eeg=True, eog=True, exclude="bads")`
4. Preprocess (optional):
   - `mne.preprocessing.find_eog_events(raw)`, `find_ecg_events(raw)`, ICA workflows
5. Spectral analysis:
   - `mne.time_frequency.psd_array_welch(...)` or `psd_array_multitaper(...)`
6. Return structured results from your MCP (Model Context Protocol) service endpoint.

### CLI fallback
- Use `mne` command wrapper when import-time overhead or environment isolation is needed.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `load_raw`
  - Load raw recordings from FIF/EDF/BDF/BrainVision.
  - Maps to `mne.io.read_raw_*`.

- `read_info`
  - Read metadata/header info without full processing.
  - Maps to `mne.io.read_info`.

- `events_detect`
  - Detect or load event markers.
  - Maps to `mne.find_events`, `mne.read_events`, `mne.merge_events`.

- `channels_pick`
  - Build channel selections by modality/type.
  - Maps to `mne.pick_types`.

- `preprocess_eog_ecg`
  - EOG/ECG event detection and projection helpers.
  - Maps to `mne.preprocessing.find_eog_events`, `find_ecg_events`, `compute_proj_eog`, `compute_proj_ecg`.

- `ica_workflow`
  - Artifact decomposition/removal pipeline.
  - Maps to `mne.preprocessing.ICA`, `EOGRegression`.

- `psd_compute`
  - Power spectral density calculations.
  - Maps to `mne.time_frequency.psd_array_welch`, `psd_array_multitaper`.

- `tfr_compute`
  - Time-frequency decomposition.
  - Maps to `tfr_morlet`, `tfr_multitaper`, `csd_multitaper`.

- `viz_diagnostics` (optional/headless-sensitive)
  - Event/covariance/alignment diagnostic plotting.
  - Maps to `mne.viz.plot_events`, `plot_cov`, `plot_bem`, `plot_alignment`.

- `cli_exec` (fallback)
  - Run `mne` subcommands for isolated or heavyweight tasks.

---

## 5) Common Issues and Notes

- **Complexity:** MNE-Python is feature-rich; keep endpoint contracts narrow and typed.
- **Import overhead:** First import can be non-trivial; consider lazy-loading per endpoint.
- **GUI dependencies:** Visualization endpoints may fail in headless servers unless backend is configured.
- **Optional packages:** Some analyses silently require extras (`sklearn`, `h5py`, `nibabel`, etc.).
- **Performance:** Large FIF files and TFR/ICA jobs are memory/CPU intensive; set resource limits.
- **Reproducibility:** Pin MNE + NumPy/SciPy versions in deployment.
- **Risk profile:** Import feasibility is moderate (~0.72); keep CLI fallback available.
- **Data handling:** Validate paths, file formats, and channel metadata before heavy processing.

---

## 6) Reference Links / Documentation

- MNE-Python repository: https://github.com/mne-tools/mne-python
- MNE official docs: https://mne.tools/stable/index.html
- MNE API reference: https://mne.tools/stable/python_reference.html
- MNE command-line tools: https://mne.tools/stable/overview/command_line.html