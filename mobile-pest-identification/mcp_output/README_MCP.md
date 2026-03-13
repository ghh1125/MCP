# mobile-pest-identification MCP (Model Context Protocol) Service README

## 1) Project Introduction

`mobile-pest-identification` is a lightweight pest detection/classification project based on the IP102 dataset assets and mobile-oriented model configuration (`src/model/pest/mobile.yaml`).  
This MCP (Model Context Protocol) service wrapper is intended to expose the core Python inference utilities as callable service tools for LLM-driven workflows.

Main capabilities (from repository analysis):
- Pest detection/inference via utility classes:
  - `Detector`
  - `PestDetector`
- Supporting utility functions:
  - `asklr()`
  - `custom_split(m)`

Repository: https://github.com/wikilimo/mobile-pest-identification

---

## 2) Installation Method

### Prerequisites
- Python 3.9+ recommended
- `pip` and virtual environment tooling

### Install Steps
1. Clone repository:
   git clone https://github.com/wikilimo/mobile-pest-identification.git  
   cd mobile-pest-identification

2. Create and activate virtual environment:
   python -m venv .venv  
   source .venv/bin/activate  
   (Windows PowerShell: .venv\Scripts\Activate.ps1)

3. Install dependencies:
   pip install -r requirements.txt

Notes:
- No `pyproject.toml`/`setup.py` detected; installation is requirements-based.
- If GPU inference is desired, install the correct CUDA-enabled build of relevant ML frameworks manually.

---

## 3) Quick Start

Typical Python usage pattern for MCP (Model Context Protocol) service integration:

from src.utils import Detector, PestDetector, custom_split

# initialize detector (constructor args depend on runtime/model setup)
detector = Detector()
pest_detector = PestDetector()

# optional utility usage
result = custom_split("sample_input")

# run inference through detector instance methods exposed by the class
# (use your image path / tensor input according to class implementation)

Practical MCP (Model Context Protocol) service pattern:
- Tool handler receives image path or image bytes
- Handler calls `PestDetector`/`Detector`
- Handler returns structured JSON (label, confidence, optional bbox/classes)

Because CLI entry points are not defined in the repository metadata, use Python module imports directly for service integration.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service endpoints for this repository:

1. `pest_detect`
- Purpose: Run model inference on an input image
- Input: `image_path` or binary image payload
- Output: Predicted pest label(s), confidence score(s), optional detection metadata

2. `pest_detector_init`
- Purpose: Initialize detector/model resources (warm start)
- Input: optional model/config path (e.g., mobile YAML)
- Output: initialization status, loaded model info

3. `dataset_custom_split`
- Purpose: Utility split/transformation using `custom_split(m)`
- Input: `m` (string/object depending on implementation)
- Output: split/processed result

4. `health_check`
- Purpose: Validate runtime readiness
- Input: none
- Output: Python/dependency/model availability status

Note: Actual function signatures beyond discovered AST metadata are limited; align endpoint schema with your wrapper implementation.

---

## 5) Common Issues and Notes

- Dependency ambiguity:
  - Exact package versions are only in `requirements.txt`; ensure strict install from file.
- Import feasibility risk is medium:
  - Analysis indicates moderate integration complexity (`import_feasibility: 0.42`).
- Model/runtime mismatch:
  - If inference fails, verify model config (`src/model/pest/mobile.yaml`) and weight paths.
- Path issues:
  - Dataset index files are in `ip102_v1.1/` (`train.txt`, `val.txt`, `test.txt`).
- Performance:
  - CPU inference may be slow for large batches; use GPU where possible.
- Service robustness:
  - Add request validation, timeout controls, and graceful fallback errors in MCP (Model Context Protocol) handlers.

---

## 6) Reference Links or Documentation

- GitHub repository: https://github.com/wikilimo/mobile-pest-identification
- Top-level README (project): `README.md`
- Requirements list: `requirements.txt`
- Core utility module: `src/utils.py`
- Class labels: `src/IP102_classes.txt`
- Model config: `src/model/pest/mobile.yaml`
- Dataset split files:
  - `ip102_v1.1/train.txt`
  - `ip102_v1.1/val.txt`
  - `ip102_v1.1/test.txt`

If you want, I can also provide a ready-to-use MCP (Model Context Protocol) service manifest and a minimal `tool -> function` mapping spec for `Detector`/`PestDetector`.