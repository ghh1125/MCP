# climlab MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps key `climlab` capabilities into MCP (Model Context Protocol)-friendly endpoints for climate modeling workflows.  
It is designed for developers who want to:

- Build and run simple climate models (especially EBM and column models)
- Compute insolation diagnostics
- Access thermodynamic helper functions
- Read core constants and model metadata
- Orchestrate process-based simulations with `Process` / `TimeDependentProcess`

Primary library: https://github.com/climlab/climlab

---

## 2) Installation Method

### System requirements
- Python 3.9+ recommended
- `numpy`, `scipy` required
- Optional: `xarray`, `matplotlib`, `netCDF4`, `numba`
- Optional advanced radiation: Fortran-compiled RRTMG extensions

### Install with pip
- pip install climlab

### Optional extras (as needed)
- pip install xarray matplotlib netCDF4 numba

### For development setup (from source)
- git clone https://github.com/climlab/climlab
- cd climlab
- pip install -e .

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) workflow
1. Initialize the service runtime.
2. Call model constructor endpoint (e.g., EBM or column model).
3. Step model forward in time.
4. Retrieve diagnostics/state fields.
5. Optionally call utility endpoints (insolation, thermo, constants).

### Minimal example flow
- Create an EBM model instance
- Integrate for N timesteps
- Fetch temperature field and energy budget diagnostics
- Compute reference insolation for given latitude/day
- Compare model output against insolation/thermo helpers

---

## 4) Available Tools and Endpoints List

Recommended endpoint surface for this repository:

- `models.create_ebm`
  - Create `EBM`, `EBM_annual`, `EBM_seasonal`, or related variants.
- `models.create_column`
  - Create `GreyRadiationModel`, `RadiativeConvectiveModel`, or `BandRCModel`.
- `models.step`
  - Advance a model using `TimeDependentProcess` stepping.
- `models.integrate`
  - Run multi-step integration and return selected diagnostics.
- `models.get_state`
  - Return state variables (`Field`) with domain metadata.
- `models.get_diagnostics`
  - Return process diagnostics and energy-budget outputs.

- `insolation.daily`
  - Wrapper for daily insolation calculation.
- `insolation.annual_mean`
  - Wrapper for annual-mean insolation calculation.

- `thermo.clausius_clapeyron`
- `thermo.qsat`
- `thermo.mixing_ratio_from_vapor_pressure`
- `thermo.vapor_pressure_from_specific_humidity`
  - Stateless thermodynamic utilities.

- `constants.list`
  - Enumerate available physical constants.
- `constants.get`
  - Fetch constant value by name.

- `domain.describe`
  - Summarize axes/domains (`Axis`, `Domain`, atmosphere/ocean slabs).
- `health.check`
  - Verify import/runtime readiness, including optional modules.

---

## 5) Common Issues and Notes

- RRTMG-related functionality may fail without compiled Fortran extensions.
- Some scientific workflows expect `xarray` for richer labeled output.
- Numerical performance can vary by grid size and subprocess complexity.
- Insolation APIs exist in both `climlab.radiation.insolation` and `climlab.solar.insolation`; keep endpoint mapping explicit.
- Keep model objects session-scoped; avoid unnecessary re-instantiation for repeated stepping.
- If running in constrained environments, disable heavy optional endpoints first (RRTMG, plotting-related paths).

---

## 6) Reference Links / Documentation

- Repository: https://github.com/climlab/climlab
- Package docs source: `docs/source` in repository
- Core modules to review:
  - `climlab/process/process.py`
  - `climlab/process/time_dependent_process.py`
  - `climlab/model/ebm.py`
  - `climlab/model/column.py`
  - `climlab/radiation/insolation.py`
  - `climlab/utils/thermo.py`
  - `climlab/utils/constants.py`
- Tests for usage patterns:
  - `climlab/tests/test_ebm.py`
  - `climlab/tests/test_rcm.py`
  - `climlab/tests/test_insolation.py`
  - `climlab/tests/test_rrtm.py`