# Tellurium MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core **Tellurium** capabilities for computational biology workflows, including:

- Loading and simulating models (Antimony, SBML, CellML)
- Converting between model formats
- Running SED-ML and COMBINE/OMEX archives
- Parameter scan and stochastic/sensitivity analysis helpers
- Plotting and result export utilities

Repository: https://github.com/sys-bio/tellurium

---

## 2) Installation

### Requirements

Core Python dependencies (from repository analysis):

- numpy
- scipy
- matplotlib
- pandas
- libroadrunner
- antimony
- phrasedml
- python-libsbml
- python-libsedml

Optional:

- plotly (interactive plotting)
- ipywidgets (notebook UI helpers)

### Install Steps

1. Create and activate a virtual environment.
2. Install Tellurium and required scientific stack.
3. If needed, install optional plotting/notebook packages.

Typical commands:

- `pip install tellurium`
- or from source repo: `pip install -r requirements.txt && pip install -e .`

---

## 3) Quick Start

### Basic model load + simulation

Use core Tellurium APIs exposed by the service:

- `loada(antimony_str)` / `loadAntimonyModel(antimony_str)`
- `loadSBMLModel(sbml_str)`
- `simulate(...)` on returned RoadRunner model
- `plotArray(result)` or plotting API

Example flow:

1. Send Antimony model text to `loada`.
2. Simulate time course (`model.simulate(0, 100, 1000)`).
3. Return numeric result and optional figure output.

### Format conversion

Common conversions:

- `antimonyToSBML`
- `sbmlToAntimony`
- `antimonyToCellML`
- `cellmlToSBML`

### SED-ML / COMBINE archive execution

- `executeSEDML(inputStr, workingDir, ...)`
- `executeCombineArchive(omexPath, ...)`
- `convertCombineArchive(location)` / `convertAndExecuteCombineArchive(location)`

---

## 4) Available Tools and Endpoints

Recommended MCP (Model Context Protocol) service endpoints (mapped to Tellurium functions):

- `health`
  - Liveness/readiness check, version info.

- `version_info`
  - Returns `getTelluriumVersion()` and dependency/runtime details.

- `load_model`
  - Inputs: `format` (`antimony|sbml|cellml`), `content`
  - Uses: `loada`, `loadSBMLModel`, `loadCellMLModel`

- `simulate_timecourse`
  - Inputs: model handle, start/end/points, selections
  - Runs model simulation and returns table/series output.

- `convert_model`
  - Inputs: source format + content, target format
  - Uses conversion APIs (`antimonyToSBML`, `sbmlToAntimony`, etc.).

- `run_sedml`
  - Inputs: SED-ML content/path + working directory/options
  - Uses: `executeSEDML`

- `run_omex`
  - Inputs: OMEX path/options
  - Uses: `executeCombineArchive`, `convertCombineArchive`

- `parameter_scan`
  - Uses Tellurium analysis classes (`ParameterScan`, `ParameterScan2D`, `SteadyStateScan`).

- `stochastic_simulation`
  - Uses stochastic helpers (`StochasticSimulationModel`, distributed helpers).

- `sensitivity_analysis`
  - Uses `SensitivityAnalysis` utilities.

- `plot_results`
  - Uses plotting APIs (`plotArray`, plotting engine abstractions).
  - Supports matplotlib by default; plotly optional.

- `archive_utils`
  - COMBINE archive utilities:
  - `extractFileFromCombineArchive`, `addFileToCombineArchive`, `createCombineArchive`

---

## 5) Common Issues and Notes

- Native/scientific dependencies can be the hardest part (`libroadrunner`, `libsbml`, `libsedml`).
- Prefer isolated environments (venv/conda) to avoid binary conflicts.
- Some advanced notebook utilities require Jupyter/ipywidgets.
- Plotting backend differences:
  - headless servers may need non-interactive backends.
- Large OMEX/SED-ML workflows can be memory/CPU heavy; set execution limits in MCP (Model Context Protocol) host.
- Repo includes legacy/deprecated modules under `tellurium/dev/deprecated`; avoid for new integrations.
- AST scan shows no dedicated CLI entry points; service integration should be Python API-driven.

---

## 6) References

- Main repository: https://github.com/sys-bio/tellurium
- Root README: `README.md` in repo
- Documentation folder: `docs/`
- SED-ML notes: `docs/sedml.md`
- Tests/examples for behavior reference:
  - `tellurium/tests/`
  - `examples/notebooks-py/`
  - `examples/tellurium-files/`