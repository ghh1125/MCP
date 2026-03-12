# GStools MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core capabilities of **GStools** for practical geostatistical workflows in LLM/tooling environments.

Main functions:
- Covariance model creation (Gaussian, Exponential, Matern, Stable, etc.)
- Random field simulation (SRF, conditioned SRF, Fourier/randomization engines)
- Variogram estimation and model fitting
- Kriging interpolation (Simple, Ordinary, Universal, External Drift, Detrended)
- Data normalization and field transformations
- Export helpers (VTK/PyVista/structured outputs)

Repository: https://github.com/GeoStat-Framework/GStools

---

## 2) Installation Method

### Requirements
- Python 3.10+ (recommended modern Python)
- Required: `numpy`, `scipy`
- Optional (feature-dependent): `matplotlib`, `meshio`, `pyevtk`, `emcee`, `hankel`, `gstools-cython`

### Install
- Core install:
  `pip install gstools`
- With common extras/tools:
  `pip install gstools matplotlib meshio pyevtk`

If you are developing the MCP (Model Context Protocol) service wrapper itself, also install your MCP runtime/server dependencies in the same environment.

---

## 3) Quick Start

### A. Create a covariance model and simulate a random field
import gstools as gs

model = gs.Gaussian(dim=2, var=1.0, len_scale=10.0)
srf = gs.SRF(model, seed=42)
field = srf((range(100), range(100)))  # structured grid

### B. Estimate an empirical variogram and fit a model
import numpy as np
import gstools as gs

pos = np.random.rand(2, 300) * 100.0
vals = np.random.randn(300)

bin_center, gamma = gs.vario_estimate(pos, vals)
fit_model = gs.Stable(dim=2)
fit_model.fit_variogram(bin_center, gamma)

### C. Ordinary kriging
import gstools as gs

model = gs.Exponential(dim=2, var=0.5, len_scale=15)
ok = gs.krige.Ordinary(model, cond_pos=[[0, 10, 20], [0, 5, 10]], cond_val=[1.2, 0.7, 1.0])
kriged, krige_var = ok((range(50), range(50)))

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `covmodel.list_models`  
  Return supported covariance families (Gaussian, Matern, Exponential, etc.).

- `covmodel.create`  
  Create/validate a covariance model with parameters (`dim`, `var`, `len_scale`, anisotropy/rotation, nugget).

- `variogram.estimate`  
  Compute empirical variogram (`vario_estimate`, optional directional/axis variants).

- `variogram.fit`  
  Fit covariance parameters from empirical variogram (`fit_variogram`, `fit_variogram_auto`).

- `field.simulate`  
  Generate random fields with `SRF` on structured/unstructured coordinates.

- `field.simulate_conditioned`  
  Generate conditioned random fields (`CondSRF`) using kriging constraints.

- `kriging.interpolate`  
  Run kriging methods: Simple, Ordinary, Universal, ExternalDrift, Detrended, DetrendedOrdinary.

- `normalizer.apply`  
  Apply normalizers (LogNormal, BoxCox, YeoJohnson, Modulus, Manly).

- `transform.apply`  
  Apply post-processing transforms (binary, discrete, zinnharvey, normal-to-lognormal, forced moments).

- `export.to_vtk` / `export.to_pyvista` / `export.to_structured`  
  Export simulation/interpolation outputs for visualization and downstream tools.

---

## 5) Common Issues and Notes

- Missing optional dependencies: export/plot/MCMC features may fail unless related packages are installed.
- Large grids can be memory-heavy; prefer chunking/downsampling for big 3D jobs.
- Kriging matrix solves may be slow/unstable with poor variogram fits or near-duplicate points.
- Use consistent coordinate units with `len_scale` and variogram bins.
- For reproducibility, always set random seeds in SRF/generator workflows.
- `gstools-cython` can improve performance in compute-heavy scenarios.

---

## 6) Reference Links / Documentation

- Main repository: https://github.com/GeoStat-Framework/GStools
- Project README: https://github.com/GeoStat-Framework/GStools/blob/main/README.md
- Changelog: https://github.com/GeoStat-Framework/GStools/blob/main/CHANGELOG.md
- Contributing: https://github.com/GeoStat-Framework/GStools/blob/main/CONTRIBUTING.md
- Examples folder: https://github.com/GeoStat-Framework/GStools/tree/main/examples
- Source package: https://github.com/GeoStat-Framework/GStools/tree/main/src/gstools