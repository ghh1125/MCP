# Tellurium MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service wraps core Tellurium capabilities for systems biology modeling and simulation.  
It is designed for developer workflows that need to:

- Load and simulate biochemical models (Antimony/SBML)
- Run SED-ML and COMBINE/OMEX simulation experiments
- Convert between model and archive formats
- Perform parameter scans and steady-state analyses
- Produce plots via configurable plotting backends

Core modules used by this service include:

- `tellurium/tellurium.py` (high-level API: `loada`, `loads`, `loadSBMLModel`, etc.)
- `tellurium/roadrunner/extended_roadrunner.py` (`ExtendedRoadRunner`)
- `tellurium/sedml/tesedml.py` (`executeSEDML`, `executeCombineArchive`)
- `tellurium/teconverters/*` (Antimony/SBML and OMEX conversions)
- `tellurium/analysis/parameterscan.py` (`ParameterScan`, `SteadyStateScan`)

---

## 2) Installation Method

### Prerequisites

- Python 3.x
- Scientific stack: `numpy`, `scipy`, `matplotlib`, `pandas`
- Modeling/simulation libs: `libroadrunner`, `antimony`, `phrasedml`, `python-libsbml`
- Optional: `plotly`, `ipywidgets`, `jupyter`

### Recommended install

1. Create and activate a virtual environment
2. Install Tellurium and dependencies with pip

Example package set:

- `tellurium`
- `numpy`
- `scipy`
- `matplotlib`
- `pandas`
- `plotly` (optional)

If binary dependencies (e.g., RoadRunner/libSBML) fail to build, prefer platform wheels/conda packages.

---

## 3) Quick Start

### Load and simulate a model

Use Tellurium high-level API (`loada`) to load Antimony text, then simulate and inspect results.

Typical flow:

1. Import `tellurium as te`
2. `rr = te.loada(<antimony_model_text>)`
3. `result = rr.simulate(start, end, points)`
4. Plot via `te.plot(...)` or `rr.plot()`

### Run SED-ML / OMEX execution

Use:

- `executeSEDML(...)` for SED-ML documents
- `executeCombineArchive(...)` for COMBINE archives

This enables reproducible experiment execution directly from standards-based files.

### Convert formats

Use converter utilities:

- `antimonyToSBML(...)`
- `sbmlToAntimony(...)`
- `inlineOmexToCombineArchive(...)`
- `combineArchiveToInlineOmex(...)`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `model.load_antimony`
  - Wraps `te.loada`
  - Input: Antimony string
  - Output: model/session handle + metadata

- `model.load_sbml`
  - Wraps `te.loadSBMLModel`
  - Input: SBML string/path
  - Output: model/session handle

- `simulation.run_timecourse`
  - Uses `ExtendedRoadRunner.simulate`
  - Input: model handle, start/end/points, selected variables
  - Output: simulation matrix/JSON series

- `simulation.steady_state`
  - Uses RoadRunner steady-state routines
  - Input: model handle
  - Output: steady-state values/status

- `sedml.execute`
  - Wraps `executeSEDML`
  - Input: SED-ML path/content + referenced models
  - Output: execution reports and datasets

- `omex.execute`
  - Wraps `executeCombineArchive`
  - Input: OMEX archive path/bytes
  - Output: experiment outputs, logs, status

- `convert.antimony_to_sbml`
  - Wraps `antimonyToSBML`
  - Input: Antimony
  - Output: SBML

- `convert.sbml_to_antimony`
  - Wraps `sbmlToAntimony`
  - Input: SBML
  - Output: Antimony

- `convert.inline_omex_to_archive`
  - Wraps `inlineOmexToCombineArchive`
  - Input: inline OMEX text
  - Output: OMEX archive artifact

- `convert.archive_to_inline_omex`
  - Wraps `combineArchiveToInlineOmex`
  - Input: OMEX archive
  - Output: inline OMEX text

- `analysis.parameter_scan`
  - Wraps `ParameterScan`
  - Input: model handle + parameter ranges
  - Output: scan results/plots

- `analysis.steady_state_scan`
  - Wraps `SteadyStateScan`
  - Input: model handle + scan definition
  - Output: scan report

- `plot.render`
  - Wraps plotting API (`plot`, `show`, `nextFigure`)
  - Input: datasets + backend options
  - Output: figure object or serialized plot artifact

---

## 5) Common Issues and Notes

- Binary dependency issues  
  `libroadrunner`, `antimony`, and `python-libsbml` may require compatible wheels/system libs.

- Environment consistency  
  Use isolated virtual environments; pin versions for reproducible behavior.

- Headless/server runtime  
  Configure matplotlib backend for non-GUI environments.

- Large OMEX/SED-ML workloads  
  Execution time and memory use can grow significantly; enforce resource/time limits in service layer.

- Input validation and safety  
  Validate uploaded model/archive content and file paths. Treat external archives as untrusted input.

- Import feasibility  
  Project analysis indicates good import feasibility, but medium complexity/intrusiveness for deep integration.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/sys-bio/tellurium
- Main package docs/source: `tellurium/`
- Examples:
  - `examples/notebooks-py/`
  - `examples/tellurium-files/`
- SED-ML module: `tellurium/sedml/tesedml.py`
- Converters: `tellurium/teconverters/`
- Tests: `tellurium/tests/`