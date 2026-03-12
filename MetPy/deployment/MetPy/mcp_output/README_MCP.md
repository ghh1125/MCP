# MetPy MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core capabilities from [MetPy](https://github.com/Unidata/MetPy) to provide meteorological computation and data-processing tools for LLM-driven workflows.

Primary service functions:
- Thermodynamic diagnostics (e.g., LCL/LFC/EL, CAPE/CIN, mixing ratio, equivalent potential temperature)
- Kinematic diagnostics (e.g., vorticity, divergence, advection, deformation, frontogenesis)
- Basic wind/temperature transforms (wind speed/direction/components, potential temperature)
- Forecast/stability indices (e.g., Showalter, K, Lifted, Total Totals, bulk shear, SRH)
- Station/radar ingestion (METAR parsing, NEXRAD Level II/III readers)
- Interpolation/gridding (station-to-grid workflows)
- xarray + units integration via Pint for safer scientific calculations

---

## 2) Installation Method

### Requirements
Core dependencies:
- numpy
- scipy
- pint
- packaging

Common optional dependencies (enable richer workflows):
- xarray, pandas
- matplotlib, cartopy
- pyproj
- netCDF4
- pooch
- siphon

### Install
- Install from PyPI:
  pip install metpy

- Recommended extras for full scientific workflows:
  pip install metpy xarray pandas matplotlib cartopy pyproj netCDF4 pooch siphon

- For MCP (Model Context Protocol) service development:
  pip install -e .

---

## 3) Quick Start

### Basic usage flow
1. Load data (arrays, xarray objects, or text/radar files)
2. Attach/use units (Pint via `metpy.units`)
3. Run calculation endpoints
4. Return structured numeric outputs (and optional metadata)

### Example calls (service-level intent)
- Thermo:
  - `lcl`, `lfc`, `el`, `cape_cin`
  - `mixing_ratio`, `dewpoint_from_relative_humidity`, `virtual_temperature`
- Kinematics:
  - `vorticity`, `divergence`, `advection`, `absolute_vorticity`, `frontogenesis`
- Basic:
  - `wind_speed`, `wind_direction`, `wind_components`, `potential_temperature`
- IO:
  - `parse_metar_file`
  - `Level2File`, `Level3File` readers
- Interpolation:
  - `interpolate_to_grid`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoint layout for this service:

- `calc.thermo.parcel_profile`  
  Parcel temperature profile computation.

- `calc.thermo.lcl` / `calc.thermo.lfc` / `calc.thermo.el`  
  Key parcel-level heights/pressures for convective diagnosis.

- `calc.thermo.cape_cin`  
  Convective available potential energy / inhibition.

- `calc.thermo.mixing_ratio`  
  Moisture ratio diagnostics.

- `calc.thermo.dewpoint_from_relative_humidity`  
  Dewpoint from RH and temperature.

- `calc.thermo.equivalent_potential_temperature`  
  Theta-e for thermodynamic state analysis.

- `calc.kinematics.vorticity` / `divergence` / `advection`  
  Core flow and derivative diagnostics.

- `calc.kinematics.frontogenesis` / `absolute_vorticity` / `q_vector`  
  Synoptic and mesoscale diagnostics.

- `calc.kinematics.shearing_deformation` / `stretching_deformation` / `total_deformation`  
  Deformation field analysis.

- `calc.basic.wind_speed` / `wind_direction` / `wind_components`  
  Wind vector conversions.

- `calc.basic.potential_temperature`  
  Thermodynamic transform.

- `calc.indices.showalter_index` / `k_index` / `lifted_index` / `total_totals_index`  
  Stability index suite.

- `calc.indices.bulk_shear` / `storm_relative_helicity`  
  Severe-weather kinematic predictors.

- `interpolate.grid.interpolate_to_grid`  
  Station/objective analysis to grid.

- `io.metar.parse_metar_file`  
  METAR text ingestion and parsing.

- `io.nexrad.Level2File` / `io.nexrad.Level3File`  
  NEXRAD binary product readers.

- `xarray.preprocess_and_wrap` / `xarray.grid_deltas_from_dataarray`  
  Coordinate-aware xarray workflows.

---

## 5) Common Issues and Notes

- Units are mandatory for reliable science:
  - Use Pint quantities consistently to avoid silent unit errors.
- Optional stack matters:
  - Plotting/raster/map workflows need matplotlib/cartopy/pyproj.
- Radar and IO pipelines may be memory-heavy:
  - For large NEXRAD files, stream/process in chunks where possible.
- xarray interoperability:
  - Prefer coordinate-aware arrays for derivative operations (dx/dy correctness).
- No native CLI detected:
  - This repository is primarily a Python library; expose MCP (Model Context Protocol) endpoints at the service layer.
- Environment recommendations:
  - Use a dedicated virtual environment/conda env to avoid binary dependency conflicts.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/Unidata/MetPy  
- Official docs: https://unidata.github.io/MetPy/  
- Project README: https://github.com/Unidata/MetPy/blob/main/README.md  
- Contributing guide: https://github.com/Unidata/MetPy/blob/main/CONTRIBUTING.md  
- Support: https://github.com/Unidata/MetPy/blob/main/SUPPORT.md