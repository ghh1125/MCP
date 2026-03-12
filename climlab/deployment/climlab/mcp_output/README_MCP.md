# climlab MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service exposes practical climate-modeling capabilities from the `climlab` Python library through MCP (Model Context Protocol).  
It is designed for developers who want programmatic access to:

- Energy balance and column climate model workflows
- Radiation and convection parameterizations
- Insolation/orbital forcing calculations
- Thermodynamic utility calculations

Primary use cases include rapid climate experiments, sensitivity tests, and embedding scientific calculations into AI-agent workflows.

---

## 2) Installation

### Requirements

- Python 3.9+ recommended
- Required:
  - `numpy`
  - `scipy`
- Optional but useful:
  - `xarray`
  - `matplotlib`
  - `netCDF4`
  - `numba`
  - `pooch`
  - `climlab-rrtmg` compiled extensions (for RRTMG radiation tools)

### Install commands

pip install climlab

Optional extras (example set):

pip install xarray matplotlib netCDF4 numba pooch

If using advanced radiation (RRTMG), ensure compiled extensions are installed and importable in your runtime environment.

---

## 3) Quick Start

### Basic import and insolation calculation

import climlab
from climlab.radiation.insolation import daily_insolation

S = daily_insolation(lat=45, day=172)
print(S)

### Create a simple EBM model and step forward

from climlab.model.ebm import EBM

model = EBM()
model.step_forward()
print(model.global_mean_temperature)

### Use thermodynamic utilities

from climlab.utils.thermo import qsat

q = qsat(T=300., p=1000.)
print(q)

---

## 4) Available Tools and Endpoints

Suggested MCP (Model Context Protocol) service endpoints mapped to core `climlab` modules:

- `insolation.daily`
  - Wrapper for daily insolation at latitude/day/orbital settings.
- `insolation.instant`
  - Instantaneous insolation for a specific geometry/time.
- `insolation.annual_mean`
  - Annual-mean insolation diagnostic.
- `insolation.solar_longitude`
  - Solar longitude/orbital position helper.

- `model.ebm.create`
  - Create EBM-family models (`EBM`, `EBM_seasonal`, etc.).
- `model.ebm.step`
  - Advance EBM state by one or multiple timesteps.
- `model.ebm.diagnostics`
  - Return key diagnostics (e.g., global mean temperature, flux terms).

- `model.column.create`
  - Create column models (`GreyRadiationModel`, `RadiativeConvectiveModel`, `BandRCModel`).
- `model.column.step`
  - Advance column model.
- `model.column.diagnostics`
  - Return heating rates / flux outputs where available.

- `radiation.greygas.compute`
  - Run grey-gas SW/LW computations (`GreyGas`, `GreyGasSW`, `GreyGasLW`).
- `radiation.cam3.compute`
  - CAM3 radiation wrapper execution.
- `radiation.rrtmg.compute`
  - RRTMG radiation computation (requires compiled backend).

- `thermo.qsat`
  - Saturation specific humidity.
- `thermo.clausius_clapeyron`
  - Saturation vapor pressure relation.
- `thermo.pseudoadiabat`
  - Moist pseudoadiabatic profile helper.
- `thermo.vapor_pressure_from_specific_humidity`
  - Convert humidity to vapor pressure.

- `domain.global_mean`
  - Global mean for gridded fields.
- `domain.to_latlon`
  - Convert/reshape field to latitude-longitude representation.

---

## 5) Common Issues and Notes

- Compiled dependency caveat:
  - RRTMG-based tools may fail if native extensions are missing. Prefer grey-gas tools when portability matters.
- Environment consistency:
  - Use a clean virtual environment to avoid version conflicts with NumPy/SciPy.
- Performance:
  - Some process trees and radiation routines are computationally heavy; batch requests and cache repeated orbital/thermo calls.
- Data model:
  - `climlab` uses process/state abstractions (`Process`, `TimeDependentProcess`); endpoint outputs should be normalized to JSON-friendly diagnostics.
- Reliability:
  - Import feasibility is generally good, but optional modules may be unavailable depending on build/runtime platform.

---

## 6) References

- Repository: https://github.com/climlab/climlab
- Project docs (source in repo): `docs/source/`
- Key modules:
  - `climlab.process.process`
  - `climlab.process.time_dependent_process`
  - `climlab.model.ebm`
  - `climlab.model.column`
  - `climlab.radiation.insolation`
  - `climlab.utils.thermo`