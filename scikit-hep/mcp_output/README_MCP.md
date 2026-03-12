# scikit-hep MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository is the **scikit-hep meta-package**.  
As an MCP (Model Context Protocol) service, it is best used as a lightweight environment/introspection service that:

- exposes package/version metadata (`skhep.__version__`)
- reports runtime and dependency diagnostics via `skhep.show_versions()`
- provides a stable namespace for Scikit-HEP ecosystem usage

This repo does **not** expose a rich CLI or multiple computation endpoints; it is primarily a diagnostics and packaging entry point.

---

## 2) Installation

### Requirements
Core dependencies identified in the project analysis:

- numpy
- scipy
- pandas
- matplotlib
- uproot
- awkward

Python packaging is managed via `pyproject.toml`, and `requirements.txt` is present.

### Install from PyPI
pip install scikit-hep

### Install from source
pip install -e .

### Install dependencies only
pip install -r requirements.txt

---

## 3) Quick Start

### Import and check version
import skhep
print(skhep.__version__)

### Show environment and dependency versions
from skhep._show_versions import show_versions
show_versions()

Typical MCP (Model Context Protocol) integration pattern:
- create a service action like `environment.get_versions`
- map that action to `show_versions()`
- return the output as structured text for debugging/support workflows

---

## 4) Available Tools and Endpoints

Given the repository contents, practical MCP (Model Context Protocol) service endpoints are:

- `health.ping`  
  Basic liveness check for the service runtime.

- `package.get_version`  
  Returns `skhep.__version__`.

- `environment.show_versions`  
  Wraps `skhep._show_versions.show_versions()` to provide Python/platform/dependency diagnostics.

- `environment.get_core_dependencies`  
  Returns expected core dependency set (numpy, scipy, pandas, matplotlib, uproot, awkward) for validation.

Note: No native CLI commands were detected in this repository analysis.

---

## 5) Common Issues and Notes

- **Meta-package scope**: This package is intentionally small; most domain functionality lives in other Scikit-HEP projects.
- **Import errors**: Usually indicate missing scientific stack dependencies; verify installation with `pip install -r requirements.txt`.
- **Environment mismatch**: `show_versions()` should be your first debugging step in MCP (Model Context Protocol) support tickets.
- **Private module path**: `_show_versions` is underscored; for stable external APIs prefer top-level exports when available in your installed version.
- **Performance**: Service is low-complexity and low-intrusiveness; startup/import risk is low per analysis.

---

## 6) Reference Links

- Repository: https://github.com/scikit-hep/scikit-hep
- Project README: https://github.com/scikit-hep/scikit-hep/blob/main/README.md
- `pyproject.toml`: https://github.com/scikit-hep/scikit-hep/blob/main/pyproject.toml
- Scikit-HEP ecosystem: https://scikit-hep.org/