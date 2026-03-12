# MONAI MCP (Model Context Protocol) Service README

## 1) Project Introduction

This MCP (Model Context Protocol) service exposes practical, high-level MONAI capabilities for medical imaging workflows, with a focus on:

- Bundle-based workflow execution (train/infer/evaluate from config)
- Config parsing and validation
- Sliding-window inference for large 2D/3D images
- Optional access to model/dataset pipeline primitives (networks, transforms, datasets)

Best-fit usage: integrating MONAI automation into LLM-driven developer tooling with minimal custom glue code.

---

## 2) Installation Method

### Requirements

- Python >= 3.9
- Core:
  - torch
  - numpy
  - monai
- Common optional dependencies (based on your workflow):
  - nibabel, SimpleITK, pydicom, itk
  - scipy, pillow, scikit-image
  - ignite
  - mlflow, tensorboard
  - opencv-python, cucim, zarr, einops

### Install (minimal)

pip install monai torch numpy

### Install (typical medical imaging stack)

pip install monai[all]

If your environment does not resolve extras reliably, install optional packages explicitly per feature needs.

---

## 3) Quick Start

### A. Run a MONAI bundle workflow

Use the Bundle orchestration layer as the primary MCP (Model Context Protocol) surface:

- `monai.bundle.scripts.run(...)`
- `monai.bundle.scripts.verify_metadata(...)`
- `monai.bundle.scripts.verify_net_in_out(...)`
- `monai.bundle.scripts.download(...)`
- `monai.bundle.scripts.init_bundle(...)`

Typical MCP (Model Context Protocol) flow:
1. Download/init bundle
2. Parse/resolve config
3. Verify metadata/network I/O
4. Run train/infer command

### B. Parse and inspect config safely

Use `monai.bundle.config_parser.ConfigParser` and:
- `load_config_file(...)`
- `parse(...)`
- `get_parsed_content(...)`

This is the recommended path for declarative, controlled config access from tools/services.

### C. Sliding-window inference

For large volumes/WSI-style inputs:
- `monai.inferers.inferer.sliding_window_inference(...)`
- Or class-based inferers: `SlidingWindowInferer`, `SimpleInferer`

---

## 4) Available Tools and Endpoints List

Suggested MCP (Model Context Protocol) endpoints for a practical service layer:

1. `bundle.run`
- Execute a MONAI bundle workflow from config overrides.
- Backend: `monai.bundle.scripts.run`

2. `bundle.verify_metadata`
- Validate bundle metadata schema/compliance.
- Backend: `monai.bundle.scripts.verify_metadata`

3. `bundle.verify_net_io`
- Check model input/output shape and compatibility.
- Backend: `monai.bundle.scripts.verify_net_in_out`

4. `bundle.download`
- Download model bundle assets.
- Backend: `monai.bundle.scripts.download`

5. `bundle.init`
- Initialize a new bundle scaffold.
- Backend: `monai.bundle.scripts.init_bundle`

6. `config.parse`
- Load and resolve MONAI config content.
- Backend: `ConfigParser.load_config_file/parse/get_parsed_content`

7. `infer.sliding_window`
- Perform patch-based inference over large tensors/images.
- Backend: `sliding_window_inference`

8. `system.health`
- Environment and dependency diagnostics (Python/Torch/MONAI/CUDA availability).

---

## 5) Common Issues and Notes

- Dependency mismatches:
  - Many MONAI features are optional-dependency driven. Missing readers/transforms usually mean missing packages (e.g., nibabel/SimpleITK/itk).
- GPU/CUDA issues:
  - Ensure Torch CUDA build matches your driver/runtime.
- Large-volume inference performance:
  - Tune ROI size, overlap, batch size, and device placement for `sliding_window_inference`.
- Config complexity:
  - Prefer parser-based validation before runtime execution.
- Heavy automation modules:
  - `Auto3DSeg`/`nnUNet` paths are powerful but dependency-sensitive and compute-heavy.
- Reproducibility:
  - Pin MONAI + Torch versions and keep bundle configs versioned.

---

## 6) Reference Links / Documentation

- MONAI repository: https://github.com/Project-MONAI/MONAI
- MONAI docs (installation/modules/config): `docs/source/` in repository
- Bundle entrypoint: `python -m monai.bundle`
- Auto3DSeg entrypoint: `python -m monai.apps.auto3dseg`
- nnUNet entrypoint: `python -m monai.apps.nnunet`
- Key modules:
  - `monai.bundle.scripts`
  - `monai.bundle.config_parser`
  - `monai.inferers.inferer`
  - `monai.transforms.compose`
  - `monai.networks.nets`