# socialsim MCP (Model Context Protocol) Service README

## 1) Project Introduction

`socialsim` is a research-oriented analytics codebase for computing social simulation measurements and comparison metrics across platforms (Twitter, Reddit, GitHub, etc.).  
This MCP (Model Context Protocol) service wrapper is intended to expose the repository’s key workflows as callable services for:

- Running measurement pipelines
- Running metric comparisons between ground truth and simulation outputs
- Reconstructing Twitter cascades
- Extracting/transforming ground-truth data into simulation-compatible formats

Primary implementation areas:

- `december-measurements/` (main measurement + metrics pipeline)
- `data_extraction/` (data prep and cascade reconstruction)
- `github-measurements/` (GitHub-specific measurement framework)

---

## 2) Installation Method

## Prerequisites

- Python 3.x (recommend 3.8–3.10 for legacy compatibility)
- pip and/or conda
- Scientific stack dependencies (pandas, numpy, scipy, scikit-learn, matplotlib, networkx, joblib)

## Install dependencies

Use the repository requirement files (note: file names are non-standard in root):

- `pip_requirements.txt`
- `conda_requirements.txt`
- optional: `github-measurements/requirements.txt`

Typical setup flow:

1. Create and activate a virtual environment (or conda env)
2. Install pip dependencies from `pip_requirements.txt`
3. If using conda, install from `conda_requirements.txt`
4. Install any missing platform-specific libraries referenced by config files

---

## 3) Quick Start

## A. Run full measurements/metrics pipeline

Main entry script:

`python december-measurements/run_measurements_and_metrics.py`

Key callable functions (for MCP (Model Context Protocol) service mapping):

- `load_data(json_file, full_submission)`
- `run_measurement(data, measurement_name, measurement_params, ...)`
- `run_metrics(ground_truth, simulation, measurement_name, measurement_params, ...)`
- `run_all_measurements(data, measurement_params, filters, output_dir, ...)`
- `run_all_metrics(ground_truth, simulation, measurement_params, filters, ...)`
- `run_challenge_measurements(fn, full_submission, output_dir, platform, domain, scenario)`
- `run_challenge_metrics(gt_fn, sim_fn, full_submission, platform, domain, scenario)`

## B. Ground-truth extraction

`python data_extraction/extract_ground_truth_cp2.py`

Useful when preparing source data for downstream measurement/metric workflows.

## C. Twitter cascade reconstruction

`python data_extraction/twitter_cascade_reconstruction.py`

Core functions include:

- `load_data(json_file, full_submission)`
- `get_reply_cascade_root_tweet(...)`
- `full_reconstruction(data, followers)`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) services to expose:

- `health_check`
  - Confirms runtime environment and dependency availability.

- `load_submission_data`
  - Wraps `load_data(...)` from pipeline scripts.
  - Input: dataset path, submission mode flag.
  - Output: parsed in-memory dataset.

- `run_single_measurement`
  - Wraps `run_measurement(...)`.
  - Input: dataset + measurement name + params.
  - Output: one measurement result.

- `run_all_measurements`
  - Wraps `run_all_measurements(...)`.
  - Input: dataset, config, filters, output directory.
  - Output: full measurement bundle.

- `run_single_metric`
  - Wraps `run_metrics(...)`.
  - Input: ground truth + simulation + measurement spec.
  - Output: metric score(s).

- `run_all_metrics`
  - Wraps `run_all_metrics(...)`.
  - Input: paired datasets + config/filters.
  - Output: full metric evaluation set.

- `run_challenge_measurements`
  - Wraps challenge-oriented execution by platform/domain/scenario.

- `run_challenge_metrics`
  - Wraps challenge-oriented metric comparison by platform/domain/scenario.

- `extract_ground_truth`
  - Wraps extraction/transformation logic from `extract_ground_truth_cp2.py`.

- `reconstruct_twitter_cascade`
  - Wraps Twitter cascade reconstruction utilities.

---

## 5) Common Issues and Notes

- Legacy structure: repository is script-oriented and not packaged as an installable Python module (`setup.py`/`pyproject.toml` absent).
- Non-standard dependency file names: root uses `pip_requirements.txt` (not `requirements.txt`).
- Import feasibility is moderate-low in strict environments; CLI/service wrapping is usually more reliable than direct deep imports.
- Config-heavy workflows: choose correct config under `december-measurements/config/` for platform/domain/scenario.
- Performance considerations:
  - Large datasets can be memory-intensive (pandas-heavy operations).
  - Some metrics are computationally expensive; batch execution and caching are recommended.
- Plotting dependencies may be optional unless visualization is enabled.
- Ensure consistent schema between simulation and ground-truth inputs before metric comparison.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/pnnl/socialsim
- Main pipeline script: `december-measurements/run_measurements_and_metrics.py`
- Data extraction docs: `data_extraction/README.md`
- Root project docs: `README.md`
- License: `license.txt`

If you expose this as an MCP (Model Context Protocol) service, prefer stable, high-level service endpoints (load/run/extract/reconstruct) and keep platform-specific config selection explicit in request parameters.