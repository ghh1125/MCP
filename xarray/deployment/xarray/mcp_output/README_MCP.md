# xarray MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps the `xarray` API as MCP (Model Context Protocol) tools for labeled N-D scientific data workflows.

Main capabilities:
- Open/load datasets and data arrays (`open_dataset`, `open_dataarray`, `open_mfdataset`, `open_zarr`)
- Save/export data (`to_netcdf`, `save_mfdataset`)
- Combine and align data (`concat`, `merge`, `combine_by_coords`, `align`, `broadcast`)
- Compute with custom functions (`apply_ufunc`, `map_blocks`, `dot`, `cov`, `corr`)
- Optional plotting support via xarray plot accessors

Best fit: building AI/data assistants that need reliable, schema-aware operations on NetCDF/Zarr-style data.

---

## 2) Installation Method

### Recommended
- Python 3.10+
- Install core:
  - `pip install xarray numpy pandas packaging`

### Optional extras (by use case)
- Parallel/lazy compute: `dask`
- NetCDF backends: `netCDF4`, `h5netcdf`, `scipy`
- Zarr/cloud: `zarr`, `fsspec`
- Time/calendar: `cftime`
- Plotting: `matplotlib`
- Performance helpers: `bottleneck`, `numbagg`
- Sparse/remote: `sparse`, `pydap`

Example full install:
- `pip install xarray dask netCDF4 h5netcdf scipy zarr fsspec cftime matplotlib bottleneck numbagg sparse pydap`

---

## 3) Quick Start

### Minimal usage flow
1. Import xarray
2. Open dataset/data array
3. Run structure + compute operations
4. Return metadata/summary/results from MCP (Model Context Protocol) endpoint

Example operations to expose in MCP (Model Context Protocol):
- `open_dataset(path_or_url, engine=...)`
- `concat([...], dim="time")`
- `merge([...])`
- `apply_ufunc(func, obj, ...)`
- `to_netcdf(output_path)`

Useful diagnostic command:
- `python -m xarray.util.print_versions`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoint surface:

- `dataset.open`
  - Open a dataset from NetCDF/Zarr/other backend.
- `dataarray.open`
  - Open a single data array.
- `dataset.open_multi`
  - Open multiple files as one logical dataset (`open_mfdataset`).
- `dataset.load`
  - Force in-memory load from lazy backend.
- `dataset.save_netcdf`
  - Persist dataset to NetCDF.
- `dataset.save_multi`
  - Save multiple datasets (`save_mfdataset`).
- `dataset.concat`
  - Concatenate objects along a dimension.
- `dataset.merge`
  - Merge variables with coordinate alignment.
- `dataset.combine_by_coords`
  - Combine datasets based on coordinates.
- `dataset.align_broadcast`
  - Align and broadcast multiple objects.
- `compute.apply_ufunc`
  - Vectorized/custom compute on xarray objects.
- `compute.map_blocks`
  - Block-wise compute (typically with dask).
- `compute.stats`
  - Dot/cov/corr convenience operations.
- `plot.render` (optional)
  - Plot via xarray accessors when matplotlib is available.
- `system.print_versions`
  - Runtime environment/version diagnostics.

---

## 5) Common Issues and Notes

- Backend engine errors:
  - Install matching optional deps (`netCDF4`, `h5netcdf`, `scipy`, `zarr`).
- Slow or memory-heavy operations:
  - Use dask-backed arrays and chunking; avoid eager `.load()` too early.
- Time decoding/calendar mismatches:
  - Install `cftime`; verify `decode_times` behavior.
- Remote/cloud reads:
  - Ensure `fsspec` and protocol-specific packages are present.
- Plot endpoint failures:
  - Install `matplotlib` and run in an environment with display/output support.
- Compatibility checks:
  - Run `python -m xarray.util.print_versions` in bug reports and CI logs.

---

## 6) Reference Links or Documentation

- Repository: https://github.com/pydata/xarray
- Official docs: https://docs.xarray.dev/
- Main API entry: `xarray.__init__` public functions/classes
- I/O backend layer: `xarray.backends.api`
- Compute extension: `xarray.computation.apply_ufunc`
- Testing helpers (for service validation): `xarray.testing.assertions`