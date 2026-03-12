# PyPSA MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps key PyPSA capabilities as MCP (Model Context Protocol) tools for power-system modeling workflows.  
It is designed for developer use cases such as:

- Building and editing `Network` models
- Importing/exporting models (CSV, NetCDF, HDF5)
- Running optimization (`optimize`) and power flow (`pf`, `lpf`)
- Extracting post-processing statistics (e.g., supply, curtailment, capacity factor)

Core value: a clean MCP (Model Context Protocol) interface over PyPSA’s model lifecycle: **create → solve → analyze → persist**.

---

## 2) Installation Method

### Requirements

- Python `>=3.10`
- Required libraries (from project analysis):
  - `numpy`, `pandas`, `scipy`, `xarray`, `linopy`, `deprecation`, `validators`
- Optional (feature-dependent):
  - IO: `netcdf4`, `h5py`, `tables`, `cloudpathlib`
  - Geo/plot: `shapely`, `geopandas`, `networkx`, `matplotlib`, `plotly`, `cartopy`, `pydeck`
  - Solvers: `highspy`, `gurobipy`, `cplex`, `glpk`

### Install

pip install pypsa

For optimization, also install at least one solver backend (example: HiGHS).

---

## 3) Quick Start

### Typical MCP (Model Context Protocol) flow

1. Create/load a network
2. Add/update components (`add`, `madd`, `remove`)
3. Set snapshots
4. Solve (`optimize`) or run power flow (`pf` / `lpf`)
5. Read statistics and export results

### Example usage flow (conceptual)

- Create `Network`
- `set_snapshots(...)`
- `add("Bus", ...)`, `add("Generator", ...)`, `add("Load", ...)`
- `optimize(...)`
- Query statistics:
  - `energy_balance`
  - `supply`
  - `curtailment`
  - `capacity_factor`
- Export via `export_to_netcdf(...)` or `export_to_csv_folder(...)`

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints (developer-facing):

- `network.create`  
  Create an empty PyPSA `Network`.

- `network.load_csv` / `network.save_csv`  
  Import/export network from/to CSV folder.

- `network.load_netcdf` / `network.save_netcdf`  
  Import/export network from/to NetCDF.

- `network.load_hdf5` / `network.save_hdf5`  
  Import/export network from/to HDF5.

- `network.set_snapshots`  
  Configure time index for simulation/optimization.

- `network.add_component`  
  Add one component (Bus, Generator, Load, Line, Link, Store, StorageUnit, Transformer, etc.).

- `network.add_components_batch`  
  Batch add components (`madd`-style).

- `network.remove_component`  
  Remove components by type/name.

- `network.consistency_check`  
  Run model validation before solving.

- `solve.optimize`  
  Build + solve optimization model and assign solution.

- `solve.pf`  
  Run nonlinear power flow.

- `solve.lpf`  
  Run linearized power flow.

- `stats.energy_balance`  
  Compute energy balance tables.

- `stats.supply` / `stats.withdrawal`  
  Aggregate supply and withdrawal indicators.

- `stats.curtailment`  
  Calculate curtailed energy.

- `stats.capacity_factor`  
  Compute capacity factor metrics.

- `network.copy`  
  Create a copy for scenario branching.

---

## 5) Common Issues and Notes

- Solver not found: `optimize` requires a supported solver. Install and verify solver availability first.
- Optional dependency errors: IO/plot/geo features require extra packages not in minimal install.
- Time-series size: large snapshot sets can significantly increase memory and solve time.
- Data consistency: run `consistency_check` before optimization to catch schema/input issues early.
- Format choice:
  - CSV: easy diff/debug
  - NetCDF/HDF5: better for large structured datasets
- Environment isolation: use a dedicated virtual environment for reproducibility.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/PyPSA/PyPSA
- Official docs index: https://pypsa.readthedocs.io/
- User guide: https://pypsa.readthedocs.io/en/latest/user-guide/
- API docs: https://pypsa.readthedocs.io/en/latest/api/
- Examples: https://pypsa.readthedocs.io/en/latest/examples/

If you want, I can also generate a ready-to-use MCP (Model Context Protocol) tool schema (JSON) for these endpoints.