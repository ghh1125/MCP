# PyAbel MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core functionality from [PyAbel](https://github.com/PyAbel/PyAbel) to provide Abel-transform workflows through MCP (Model Context Protocol)-style tools.

Primary goals:
- Run forward/inverse Abel transforms on 2D images
- Choose among multiple transform backends (BASEX, Hansen–Law, Direct, Dasch, Daun, Lin-BASEX, rBASEX)
- Support common pre/post processing used in VMI pipelines:
  - image centering
  - radial/angular integrations

Best high-level integration point: `abel.transform.Transform`.

---

## 2) Installation Method

### Requirements
- Python 3.x
- Required libraries:
  - `numpy`
  - `scipy`
- Common optional libraries:
  - `matplotlib` (visualization/examples)
  - `pytest` (tests)

### Install commands
- Install PyAbel from PyPI:
  - `pip install pyabel`
- Or install from source repository:
  - `pip install .`

If building an MCP (Model Context Protocol) service wrapper, install your MCP server/runtime framework separately, then import PyAbel in service handlers.

---

## 3) Quick Start

### Minimal transform flow
1. Load a 2D image (NumPy array).
2. Optionally center it (`find_center`, `center_image`).
3. Run transform via `Transform` (recommended) or a specific backend function.
4. Extract distributions with VMI utilities (`radial_integration`, `angular_integration`).

### Example usage pattern
- High-level:
  - `abel.transform.Transform(image, method="hansenlaw", direction="inverse")`
- Backend-specific:
  - `basex_transform(...)`
  - `direct_transform(...)`
  - `hansenlaw_transform(...)`
  - `rbasex_transform(...)`

Recommended default for service design:
- Expose one unified endpoint using `Transform`
- Add an optional `method` parameter for backend selection
- Keep backend-specific endpoints for advanced users

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) service endpoints:

- `transform_image`
  - Main unified transform endpoint
  - Params: `image`, `method`, `direction`, method-specific options
  - Internally uses `abel.transform.Transform`

- `transform_basex`
  - BASEX backend
  - Uses `abel.basex.basex_transform`

- `transform_direct`
  - Direct numerical integration backend
  - Uses `abel.direct.direct_transform`

- `transform_hansenlaw`
  - Fast recursive Hansen–Law backend
  - Uses `abel.hansenlaw.hansenlaw_transform`

- `transform_dasch`
  - Dasch family methods
  - Options: `two_point`, `three_point`, `onion_peeling`
  - Uses functions in `abel.dasch`

- `transform_daun`
  - Daun backend with regularization-related controls
  - Uses `abel.daun.daun_transform`

- `transform_linbasex`
  - Lin-BASEX analysis flow
  - Uses `abel.linbasex.linbasex_transform`

- `transform_rbasex`
  - rBASEX backend for VMI-oriented use cases
  - Uses `abel.rbasex.rbasex_transform`

- `find_center`
  - Detect image center
  - Uses `abel.tools.center.find_center`

- `center_image`
  - Shift/recenter image
  - Uses `abel.tools.center.center_image`

- `radial_integration`
  - Extract radial intensity distribution
  - Uses `abel.tools.vmi.radial_integration`

- `angular_integration`
  - Extract angular distribution
  - Uses `abel.tools.vmi.angular_integration`

Note: No packaged CLI entry points were detected; service usage is Python API-driven.

---

## 5) Common Issues and Notes

- Input format:
  - Expect NumPy 2D arrays.
  - Validate shape/dtype in service layer before calling PyAbel.

- Centering quality matters:
  - Poor centering can significantly degrade inversion quality.
  - Prefer running `find_center` + `center_image` before transform.

- Method selection:
  - Different backends trade off speed, noise sensitivity, and reconstruction quality.
  - Provide sensible defaults (for example, `hansenlaw` or `rbasex`) and allow override.

- Performance:
  - Large images and basis-generation methods can be expensive.
  - Consider caching and async/background execution in your MCP (Model Context Protocol) service.

- Dependencies:
  - Missing `numpy/scipy` will prevent imports.
  - `matplotlib` is optional unless plotting is needed.

- Testing:
  - Repository includes extensive tests under `abel/tests`; use them as behavioral references when validating service wrappers.

---

## 6) Reference Links and Documentation

- Repository: https://github.com/PyAbel/PyAbel
- PyAbel documentation (in repo `doc/` and project docs): start from repository README/docs
- Key module entrypoint:
  - `abel/transform.py` (`Transform` class)
- Useful utility modules:
  - `abel/tools/center.py`
  - `abel/tools/vmi.py`