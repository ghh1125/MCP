# VULCAN MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core VULCAN workflows for atmospheric chemistry and photochemistry simulations (exoplanets/planetary atmospheres).  
It is designed for developer use: prepare atmospheres, run kinetics integration, regenerate chemistry functions, and inspect outputs/diagnostics.

Primary capabilities:
- Run full VULCAN simulations from config
- Build atmospheric profiles and boundary-condition inputs
- Regenerate chemistry kernels from reaction networks
- Generate auxiliary tables and flux-related outputs
- Post-process and plot results with included scripts

---

## 2) Installation Method

### Requirements
- Python 3.9+ recommended
- Required libraries:
  - numpy
  - scipy
  - matplotlib
- Optional but useful:
  - numba
  - pillow
  - astropy
  - pandas

### Install (typical)
- Clone repo: `https://github.com/exoclime/VULCAN`
- Install dependencies:
  - `pip install numpy scipy matplotlib`
  - Optional: `pip install numba pillow astropy pandas`

Because the repository does not provide `requirements.txt`/`pyproject.toml`, install dependencies manually in a virtual environment.

---

## 3) Quick Start

### Minimal run flow
1. Copy a sample config from `cfg_examples/` (for example Earth/Jupiter/HD189).
2. Adjust paths and runtime parameters in `vulcan_cfg.py` (or your copied config).
3. Run the simulation:
   - `python vulcan.py`

### Common utility runs
- Build atmosphere/preprocess profiles:
  - `python build_atm.py`
- Regenerate chemistry functions from network/thermo sources:
  - `python make_chem_funs.py`
- Produce helper tables:
  - `python tools/make_mix_table.py`
- Print/extract actinic flux info:
  - `python tools/print_actinic_flux.py`

Core modules used internally:
- `op.py` (integration/ODE solver/output logic)
- `build_atm.py` (atmosphere + initial abundance)
- `chem_funs.py` (kinetic/thermo functions)
- `store.py` (state/data containers)

---

## 4) Available Tools and Endpoints List

For this MCP (Model Context Protocol) service, expose these practical service endpoints:

- `run_simulation`
  - Purpose: Execute `vulcan.py` using a selected config
  - Input: config path, run options
  - Output: simulation outputs/logs/artifacts

- `build_atmosphere`
  - Purpose: Run `build_atm.py` preprocessing
  - Input: atmosphere template/profile settings
  - Output: generated atmospheric structure files

- `regenerate_chemistry_functions`
  - Purpose: Run `make_chem_funs.py` to rebuild chemistry code from networks
  - Input: network/thermo file paths
  - Output: regenerated chemistry function artifacts

- `make_mixing_table`
  - Purpose: Run `tools/make_mix_table.py`
  - Input: species/profile parameters
  - Output: mixing table data file

- `print_actinic_flux`
  - Purpose: Run `tools/print_actinic_flux.py`
  - Input: run output path
  - Output: actinic flux summaries

- `plot_results` (optional convenience endpoint)
  - Purpose: Invoke scripts in `plot_py/`
  - Input: result files + plot type
  - Output: figures for diagnostics/publication

---

## 5) Common Issues and Notes

- Manual dependency management required  
  No packaged installer metadata is provided.
- Config-first workflow  
  Most failures are due to incorrect paths in config/data files.
- Data-heavy repository  
  Large thermo/cross-section assets can increase startup and I/O time.
- Numerical performance  
  Long chemistry networks are computationally expensive; consider optional acceleration libs.
- Import feasibility is moderate  
  Prefer script/CLI-style execution orchestration in MCP (Model Context Protocol) services rather than deep in-process monkey-patching.
- Reproducibility  
  Keep a copy of the exact config + network files used for each run.

---

## 6) Reference Links or Documentation

- Upstream repository: https://github.com/exoclime/VULCAN
- Main project docs/readme: `README.md` (repo root)
- Config examples: `cfg_examples/`
- Thermo/network data: `thermo/`
- Atmosphere and stellar flux inputs: `atm/`
- Plot scripts: `plot_py/`
- Config parameter reference: `vulcan_cfg_README.txt`