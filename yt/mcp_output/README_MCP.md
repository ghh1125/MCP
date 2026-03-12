# yt MCP (Model Context Protocol) Service README

## 1) Project Introduction

This project provides an MCP (Model Context Protocol) service wrapper around the `yt` scientific analysis library, focused on:

- Loading simulation/mesh/particle datasets
- Inspecting dataset metadata and available fields
- Querying data from geometric selections (region, sphere, ray, slice-like selections)
- Generating quick analysis outputs (profiles, projections, slices)
- Exporting plots/images for downstream LLM or UI workflows

Primary integration surface is Python imports from `yt` (preferred), with optional fallback to the `yt` CLI.

---

## 2) Installation Method

### Requirements

Core runtime dependencies (minimum):
- numpy
- packaging
- more-itertools
- tomli (Python < 3.11)
- typing-extensions (Python < 3.11)

Common optional dependencies (recommended for full capability):
- matplotlib, scipy, h5py, unyt
- astropy, pandas, sympy
- pooch, netCDF4, imageio
- f90nml, libconf
- cartopy, shapely (geo workflows)

### Install

- Install from PyPI:
  - `pip install yt`
- For richer plotting and IO support:
  - `pip install "yt[full]"` (if your environment supports extras)
  - or manually install optional packages listed above

### Service setup

- Add this MCP (Model Context Protocol) service to your MCP host configuration.
- Configure Python environment path and working directory where data files are accessible.
- Prefer direct imports (`yt.load`, plotting classes) over shelling out to CLI.

---

## 3) Quick Start

### Basic flow

1. Load dataset via `yt.load(...)`
2. Inspect fields and metadata
3. Create a data object (e.g., all_data, sphere, region)
4. Extract arrays or compute quantities
5. Optionally create plots (`SlicePlot`, `ProjectionPlot`, `ProfilePlot`)

### Example usage flow

- Load: `yt.load("path/to/output")`
- Get global data container: `ds.all_data()`
- Access field: `ad[("gas", "density")]`
- Plot slice: `yt.SlicePlot(ds, "z", ("gas", "density"))`
- Plot projection: `yt.ProjectionPlot(ds, "z", ("gas", "density"))`
- Profile/phase diagnostics via profile plotting APIs

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoints for this service:

- `dataset.load`
  - Load dataset from path/URL and return dataset handle/id.
  - Backed by `yt.load`, plus specialized loaders (`load_uniform_grid`, `load_particles`, etc.).

- `dataset.info`
  - Return metadata: domain size, dimensionality, current time/redshift, geometry, code/frontend type.

- `dataset.fields.list`
  - List available native and derived fields.
  - Uses field registry/introspection (`FieldInfoContainer`).

- `dataset.fields.describe`
  - Return field units, sampling type, aliases, and availability notes.

- `selection.create`
  - Build selection objects: region/sphere/box/ray/cut-region.
  - Based on yt selection container APIs.

- `selection.sample`
  - Fetch field values from a saved selection; optional unit conversion and statistics.

- `analysis.quantities`
  - Common derived quantities (min/max/mean/sum, weighted stats) from data containers.

- `analysis.profile`
  - Compute 1D/2D profiles and optionally return plot artifacts (`ProfilePlot`, `PhasePlot`).

- `visualization.slice`
  - Generate slice image outputs (`SlicePlot`, off-axis slice options).

- `visualization.projection`
  - Generate projection images (`ProjectionPlot`, weighting options).

- `visualization.export`
  - Save plot/image products and return artifact paths/URIs.

- `system.health`
  - Report environment/dependency readiness (matplotlib/h5py/scipy/etc.).

---

## 5) Common Issues and Notes

- Large data performance:
  - Use constrained selections (sphere/region) instead of full-domain reads.
  - Avoid returning raw full-resolution arrays through MCP (Model Context Protocol); summarize or downsample first.

- Optional dependency gaps:
  - Missing `matplotlib` disables plotting endpoints.
  - Missing `h5py/netCDF4/astropy` may break specific frontend/data formats.

- Environment consistency:
  - Keep service Python env aligned with your local analysis env.
  - Verify `yt` version compatibility for older simulation outputs.

- Frontend complexity:
  - `yt` supports many code formats; not every format is equally tested in every environment.
  - Add format-specific validation in `dataset.load` error handling.

- Stability guidance:
  - Prefer import-based API calls over invoking `yt` CLI internals for long-term maintainability.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/yt-project/yt
- Main docs: https://yt-project.org/doc/
- Project README: https://github.com/yt-project/yt/blob/main/README.md
- API entrypoints of interest:
  - `yt.loaders` (loading)
  - `yt.data_objects.static_output.Dataset`
  - `yt.fields.derived_field.DerivedField`
  - `yt.visualization.plot_window` (Slice/Projection plotting)
  - `yt.visualization.profile_plotter` (Profile/Phase plotting)
- CLI reference (fallback): `yt` command family (`yt.utilities.command_line`)