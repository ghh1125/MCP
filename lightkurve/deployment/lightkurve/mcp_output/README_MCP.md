# Lightkurve MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core capabilities of the `lightkurve` library to support astronomy workflows around Kepler/K2/TESS data.

Main functions:
- Search and discover mission data products from MAST
- Load and process light curves
- Load and analyze target pixel files (TPFs)
- Run period analysis (Lomb-Scargle, BLS)
- Apply systematics correction (CBV, PLD, SFF, regression)
- Perform basic asteroseismology estimation

This service is best suited for programmatic scientific pipelines and notebook-based analysis.

---

## 2) Installation Method

### Requirements
Required Python dependencies (from repository analysis):
- numpy
- astropy
- scipy
- matplotlib
- requests
- astroquery

Optional (feature-dependent):
- bokeh (interactive widgets)
- pandas
- tqdm
- oktopus
- fbpca
- scikit-learn

### Install commands
- Install Lightkurve:
  pip install lightkurve

- (Optional) install common extras:
  pip install bokeh pandas tqdm scikit-learn

- Verify installation:
  python -c "import lightkurve as lk; print(lk.__version__)"

---

## 3) Quick Start

### A) Search and download a light curve
import lightkurve as lk
sr = lk.search_lightcurve("TIC 25155310", mission="TESS")
lc = sr.download()
lc = lc.remove_nans().normalize().flatten()
print(lc)

### B) Period search
pg = lc.to_periodogram(method="lombscargle")
best_period = pg.period_at_max_power
print(best_period)

### C) Pixel-level workflow
tpf_sr = lk.search_targetpixelfile("Kepler-10", mission="Kepler", cadence="long")
tpf = tpf_sr.download()
lc_from_tpf = tpf.to_lightcurve(aperture_mask="pipeline")
print(lc_from_tpf)

### D) Read local files
lc2 = lk.read("path/to/file.fits")
print(type(lc2))

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `search_lightcurve`
  - Discover light curve products by target/mission/sector/author filters.
- `search_targetpixelfile`
  - Discover target pixel products for aperture photometry workflows.
- `search_tesscut`
  - Request TESS cutout products.
- `read`
  - Unified file reader for mission-specific and generic formats.
- `lightcurve_ops`
  - Common transforms: normalize, flatten, fold, remove outliers, stitch, plot.
- `to_periodogram`
  - Create `LombScarglePeriodogram` or `BoxLeastSquaresPeriodogram`.
- `correct_systematics`
  - Apply `RegressionCorrector`, `PLDCorrector`, `SFFCorrector`, or `CBVCorrector`.
- `seismology_estimate`
  - Access `Seismology` helpers for numax/deltanu and stellar estimators.
- `interact_widget` (optional)
  - Notebook visualization via Bokeh (`show_interact_widget`).

Notes:
- The upstream project exposes these as Python APIs, not a built-in CLI.
- Map each endpoint to one MCP (Model Context Protocol) service method in your host runtime.

---

## 5) Common Issues and Notes

- Network access required:
  - Search/download operations use remote archives (MAST via astroquery/requests).
- Optional dependency pitfalls:
  - Interactive visualization requires `bokeh`.
  - Some correction workflows may rely on optional scientific packages.
- Environment:
  - Use a clean virtual environment to avoid Astropy/NumPy version conflicts.
- Performance:
  - TPF operations can be memory-heavy; prefer filtered searches and sector/cadence constraints.
- Reproducibility:
  - Pin dependency versions in production deployments.
- Testing baseline:
  - Repository includes extensive tests under `tests/`; use them as behavior reference when building MCP (Model Context Protocol) service wrappers.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/lightkurve/lightkurve
- Package docs root (in repo): `docs/source/`
- Main API modules:
  - `lightkurve.search`
  - `lightkurve.lightcurve`
  - `lightkurve.targetpixelfile`
  - `lightkurve.periodogram`
  - `lightkurve.correctors`
  - `lightkurve.seismology`
  - `lightkurve.io.read`

If you are implementing this as an MCP (Model Context Protocol) service, start by exposing `search_*`, `read`, light curve transforms, and periodogram generation first; then add correction and seismology endpoints as advanced services.