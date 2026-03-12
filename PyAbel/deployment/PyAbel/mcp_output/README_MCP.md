# PyAbel MCP (Model Context Protocol) Service README

## 1) Project Introduction

This service wraps core **PyAbel** functionality for Abel transform workflows, mainly for velocity-map imaging (VMI) and cylindrically symmetric image reconstruction.

Primary capabilities:
- Run forward/inverse Abel transforms through a unified interface (`abel.transform.Transform`)
- Select among multiple numerical methods (BASEX, rBasex, Hansen–Law, Direct, Dasch-family, Daun, lin-Basex, Nestor–Olsen, Onion-Bordas)
- Pre/post-process images (centering, symmetry handling, polar conversion, VMI distributions)

This MCP (Model Context Protocol) service is intended for developers who want programmatic transform operations with method-level control.

---

## 2) Installation Method

### Requirements
- Python 3.x
- Required: `numpy`, `scipy`
- Optional (recommended): `matplotlib` (visualization), `setuptools`

### Install from PyPI
pip install pyabel

### Install from source
pip install git+https://github.com/PyAbel/PyAbel.git

### Verify
python -c "import abel; print('PyAbel OK')"

---

## 3) Quick Start

### Minimal transform usage
import numpy as np
from abel.transform import Transform

# image: 2D numpy array (centered or centerable)
image = np.random.rand(201, 201)

# Inverse Abel transform with a selected method
result = Transform(image, method='hansenlaw', direction='inverse')
reconstructed = result.transform

### Typical preprocessing + transform flow
- Center image (`abel.tools.center`)
- Apply symmetry/quadrant strategy (`abel.tools.symmetry`)
- Run transform (`abel.transform.Transform`)
- Extract radial/VMI observables (`abel.tools.vmi`, `abel.tools.polar`)

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints:

- `transform.run`
  - Execute forward/inverse Abel transform.
  - Inputs: image array, method, direction, method options.
  - Backend: `abel.transform.Transform`.

- `transform.methods.list`
  - Return supported transform methods and brief descriptions.
  - Includes: `basex`, `rbasex`, `hansenlaw`, `direct`, `dasch`, `daun`, `linbasex`, `nestorolsen`, `onion_bordas`.

- `preprocess.center`
  - Center image before transform.
  - Backend: `abel.tools.center`.

- `preprocess.symmetry`
  - Apply symmetry and quadrant handling.
  - Backend: `abel.tools.symmetry`.

- `coords.to_polar`
  - Convert Cartesian image representation to polar.
  - Backend: `abel.tools.polar`.

- `vmi.distributions`
  - Compute radial/angular distributions and anisotropy-related quantities.
  - Backend: `abel.tools.vmi`.

- `system.health`
  - Validate runtime dependencies and basic import checks.

---

## 5) Common Issues and Notes

- **Centering is critical**: poor centering strongly degrades reconstruction quality.
- **Method choice matters**:
  - `hansenlaw`/`direct` are good general baselines.
  - `rbasex` is common for VMI-style analyses.
  - `basex`/`daun` may require basis/regularization tuning.
- **Performance considerations**:
  - Larger images and basis-generation methods can be slower.
  - Reusing cached basis data (where supported) improves throughput.
- **Numerical stability**:
  - Use appropriate smoothing/regularization for noisy data.
  - Validate outputs with synthetic or known-reference images.
- **Dependencies**:
  - Missing `numpy/scipy` will prevent core execution.
  - `matplotlib` only needed for plotting/debug visualization.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/PyAbel/PyAbel
- Main API entry point: `abel/transform.py` (`Transform` class)
- Method implementations:
  - `abel/basex.py`
  - `abel/rbasex.py`
  - `abel/hansenlaw.py`
  - `abel/direct.py`
  - `abel/dasch.py`
  - `abel/daun.py`
  - `abel/linbasex.py`
  - `abel/nestorolsen.py`
  - `abel/onion_bordas.py`
- Utilities:
  - `abel/tools/center.py`
  - `abel/tools/symmetry.py`
  - `abel/tools/polar.py`
  - `abel/tools/vmi.py`
- Examples folder: `examples/` (practical usage patterns)