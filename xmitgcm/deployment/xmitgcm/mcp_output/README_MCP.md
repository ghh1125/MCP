# xmitgcm MCP (Model Context Protocol) Service README

## 1) Project Introduction

**xmitgcm** is a Python library for reading **MITgcm** model output (MDS binary/meta format) into **xarray** datasets, with optional **dask**-backed lazy loading for large simulations.

This MCP (Model Context Protocol) service wraps xmitgcm capabilities so tools/agents can:

- Open standard MITgcm MDS datasets
- Load metadata and diagnostics definitions
- Access LLC grid model readers (including known model presets)
- Work with local and remote storage patterns (via llcreader stores)

Core functions exposed by the codebase include:

- `open_mdsdataset`
- `open_mdsdataset_from_mds_store`
- Low-level parsers such as `parse_meta_file`, `read_mds`
- LLC model access via `get_dataset`, `get_model`

---

## 2) Installation Method

### Requirements

Required Python dependencies (from analysis):

- `numpy`
- `xarray`
- `dask`
- `cachetools`

Optional but commonly useful:

- `zarr`
- `fsspec`
- `netCDF4`
- `scipy`

### Install from PyPI

pip install xmitgcm

### Install latest from GitHub

pip install git+https://github.com/MITgcm/xmitgcm.git

### Development/Test setup (typical)

- Use Python 3.11+ (repo CI includes 3.11/3.12/3.13)
- Install editable mode plus test tools as needed

pip install -e .

---

## 3) Quick Start

### Open an MITgcm MDS dataset

from xmitgcm import open_mdsdataset

ds = open_mdsdataset(data_dir="/path/to/mitgcm/output", prefix=["T", "S"])
print(ds)

### Open from an existing MDS store abstraction

from xmitgcm import open_mdsdataset_from_mds_store

ds = open_mdsdataset_from_mds_store(store=my_store)
print(ds.variables)

### Use LLC reader known model registry

from xmitgcm.llcreader.known_models import get_model

model = get_model("ECCOv4")  # example known model name
ds = model.get_dataset(varnames=["Theta"], k_levels=[0])
print(ds)

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints mapped to library functions:

- **open_mdsdataset**
  - Open MITgcm MDS output directory into an xarray Dataset.
- **open_mdsdataset_from_mds_store**
  - Build Dataset from a preconfigured MDSDataStore object.
- **parse_meta_file**
  - Parse MITgcm `.meta` file structure and dimensions.
- **read_mds**
  - Read raw MDS binary data arrays using metadata.
- **parse_available_diagnostics**
  - Parse diagnostics catalog for available model output fields.
- **get_grid_from_input**
  - Build/derive grid metadata from model inputs.
- **llc_get_model** (wrapper of `known_models.get_model`)
  - Retrieve preconfigured LLC model definitions.
- **llc_get_dataset** (wrapper of `LLCModel.get_dataset`)
  - Load LLC tiled output as xarray Dataset.
- **create_index / materialize_index**
  - Build and expand shrunk LLC index mappings for efficient subset workflows.
- **file_cache_clear** (wrapper of `file_utils.clear_cache`)
  - Clear internal file listing cache.

---

## 5) Common Issues and Notes

- **No CLI by default**: xmitgcm is primarily an importable Python API, so MCP (Model Context Protocol) service methods should call Python functions directly.
- **Large data performance**: prefer dask-backed lazy loading and subset variables/time/depth early.
- **I/O bottlenecks**: MITgcm outputs can be many files; storage latency (especially remote HTTP/object storage) strongly affects performance.
- **Optional dependencies**: install `fsspec`/`zarr`/`netCDF4` only if your workflow needs those formats/backends.
- **Metadata consistency**: ensure `.meta` and binary files are aligned; parsing errors typically indicate missing/corrupt pairs or wrong endianness/dtype assumptions.
- **Environment reproducibility**: pin versions in your deployment for stable behavior across xarray/dask updates.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/MITgcm/xmitgcm
- MITgcm project: https://mitgcm.org/
- xarray documentation: https://docs.xarray.dev/
- dask documentation: https://docs.dask.org/

If you are implementing this as an MCP (Model Context Protocol) service, keep endpoint contracts thin and map arguments closely to upstream xmitgcm function signatures for maintainability.