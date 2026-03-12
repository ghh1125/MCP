# astroML MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes practical astroML capabilities through MCP (Model Context Protocol) endpoints so LLM agents and developer tools can run astronomy-focused statistical workflows.

Main capabilities include:

- Spatial statistics and correlation analysis (`two_point`, angular correlation, bootstrap)
- Adaptive density estimation (Bayesian Blocks)
- Time-series period search (Lomb–Scargle, multiterm periodograms)
- Regression and modeling helpers (linear/polynomial/basis regression)
- MST-based clustering
- Dataset fetch/access helpers (SDSS, RR Lyrae, LIGO, NASA atlas, etc.)
- Generic statistical utilities (binned statistics, random-state helpers)

Repository: https://github.com/astroML/astroML

---

## 2) Installation Method

### Requirements

Core dependencies:

- numpy
- scipy
- scikit-learn
- matplotlib
- astropy

Optional/operational:

- pandas (some workflows)
- pytest stack (tests)
- Internet access for remote dataset fetchers

### Install

- Install astroML from PyPI:
  pip install astroML

- Or install from source:
  pip install git+https://github.com/astroML/astroML.git

- For local development:
  git clone https://github.com/astroML/astroML.git  
  cd astroML  
  pip install -e .

---

## 3) Quick Start

### Minimal service usage flow

1. Start your MCP (Model Context Protocol) host/runtime.
2. Register this astroML service.
3. Call endpoints with structured parameters.

### Example calls (conceptual)

- Correlation analysis:
  call `correlation.two_point` with sample coordinates, bin edges, and estimator options.
- Adaptive binning:
  call `density.bayesian_blocks` with event/time/value arrays and fitness type.
- Period search:
  call `time_series.lomb_scargle` with times, observations, errors, and frequency grid.
- Dataset load:
  call `datasets.fetch_sdss_specgals` (or related fetchers) with cache/data-home settings.

### Python-side direct usage (if needed)

Import from `astroML` modules directly (for local scripts/tests), e.g. correlation, density_estimation, time_series, stats, datasets.

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoint map:

- `correlation.two_point`  
  Compute 2-point correlation function from point samples.
- `correlation.bootstrap_two_point`  
  Bootstrap uncertainty estimation for 2-point correlation.
- `correlation.two_point_angular`  
  Angular 2-point correlation on spherical data.
- `correlation.uniform_sphere`  
  Generate uniform random points on a sphere.

- `density.bayesian_blocks`  
  Adaptive histogram/bin segmentation via Bayesian Blocks.
- `density.xdeconv`  
  Extreme deconvolution helpers for noisy mixtures (advanced).

- `time_series.lomb_scargle`  
  Lomb–Scargle periodogram.
- `time_series.lomb_scargle_bootstrap`  
  Bootstrap significance estimates for periodograms.
- `time_series.multiterm_periodogram`  
  Multi-harmonic periodogram fitting.
- `time_series.search_frequencies`  
  Frequency-grid search utilities.

- `linear_model.linear_regression`  
  Linear regression wrapper.
- `linear_model.polynomial_regression`  
  Polynomial regression convenience model.
- `linear_model.basis_function_regression`  
  Basis-function expansion regression.

- `clustering.hierarchical_mst`  
  MST-based hierarchical clustering.
- `clustering.graph_segments`  
  Extract graph segments from clustering structure.

- `stats.binned_statistic`  
  1D binned statistic.
- `stats.binned_statistic_2d`  
  2D binned statistic.
- `stats.binned_statistic_dd`  
  N-dimensional binned statistic.

- `datasets.fetch_dr7_quasar`
- `datasets.fetch_rrlyrae_mags`
- `datasets.fetch_sdss_specgals`
- `datasets.fetch_nasa_atlas`
- `datasets.fetch_ligo_large`  
  Dataset access/fetch endpoints (network/cache aware).

- `utils.check_random_state`
- `utils.log_multivariate_gaussian`
- `utils.split_samples`  
  Shared utility endpoints.

---

## 5) Common Issues and Notes

- No built-in CLI was detected; expose features as MCP (Model Context Protocol) service endpoints.
- Many dataset tools require network access on first fetch; configure cache directory to avoid repeated downloads.
- Some algorithms are compute-heavy (periodograms, bootstrap, clustering on large samples); enforce size/time limits in service layer.
- Keep NumPy/SciPy/scikit-learn/astropy versions compatible in a single environment.
- For production service stability:
  - validate array shapes/dtypes at endpoint boundary,
  - cap maximum input length,
  - add request timeouts and cancellation,
  - log provenance (dataset version, parameter set, random seed).

---

## 6) Reference Links and Documentation

- Source repository: https://github.com/astroML/astroML
- Package docs hub: https://www.astroml.org/
- Code areas of interest:
  - `astroML/correlation.py`
  - `astroML/density_estimation/bayesian_blocks.py`
  - `astroML/time_series/periodogram.py`
  - `astroML/linear_model/linear_regression.py`
  - `astroML/clustering/mst_clustering.py`
  - `astroML/datasets/`
  - `astroML/stats/_binned_statistic.py`

If you want, I can also generate a ready-to-use MCP (Model Context Protocol) service manifest (tool schema + input/output contracts) for these endpoints.