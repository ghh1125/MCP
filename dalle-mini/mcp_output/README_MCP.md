# dalle-mini MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository can be exposed as an MCP (Model Context Protocol) service for text-to-image generation based on the `dalle-mini` stack (JAX/Flax + Transformers).  
It is best suited for:

- Prompt-to-image generation via a callable backend function
- Local inference UI (Gradio or Streamlit)
- Model training/fine-tuning pipelines (advanced usage)

Core callable surface for service integration:
- `get_images_from_prompt` in:
  - `app/gradio/backend.py`
  - `app/streamlit/backend.py`

---

## 2) Installation Method

### Prerequisites
- Python 3.8+ (recommended 3.9/3.10)
- `pip` and virtual environment tooling
- JAX-compatible runtime (CPU/GPU/TPU depending on your setup)

### Install dependencies
This repo uses `setup.cfg`/`setup.py` style packaging.

1. Create and activate a virtual environment
2. Install package and runtime deps

Example:
- `pip install -U pip setuptools wheel`
- `pip install -e .`
- `pip install jax flax transformers numpy Pillow datasets sentencepiece tokenizers`
- Optional UI deps:
  - `pip install gradio`
  - `pip install streamlit`

If you plan to train:
- `pip install wandb` (optional tracking)
- Install additional optimizer extras in `tools/train/scalable_shampoo` as needed.

---

## 3) Quick Start

### A. Run inference UI
- Gradio:
  - `python app/gradio/app.py`
- Streamlit:
  - `streamlit run app/streamlit/app.py`

### B. Call main inference function from your MCP (Model Context Protocol) service
Use `get_images_from_prompt(prompt, ...)` from either backend module as your tool handler target.  
Typical flow:
1. Receive prompt from MCP (Model Context Protocol) client
2. Normalize/process text
3. Run model generation
4. Return images (or image paths/base64 payloads) to client

### C. Training entrypoint
- `python tools/train/train.py`
Use config files under `tools/train/config/*/config.json`.

---

## 4) Available Tools and Endpoints List

Recommended MCP (Model Context Protocol) service tools:

1. `generate_images`
- Backed by: `get_images_from_prompt`
- Input: text prompt (+ optional generation parameters)
- Output: generated image set (format defined by your service layer)

2. `normalize_prompt` (optional utility)
- Backed by: `normalize_text` in `src/dalle_mini/model/text.py`
- Input: raw prompt
- Output: cleaned/normalized prompt

3. `train_model` (advanced/admin)
- Backed by: `tools/train/train.py:main`
- Input: training config path and runtime flags
- Output: training job status/artifacts

4. `health_check`
- Custom service endpoint
- Verifies model/tokenizer load and runtime readiness

---

## 5) Common Issues and Notes

- JAX installation is environment-specific; install the correct wheel for CPU/GPU/TPU.
- First model load can be slow and memory-heavy.
- Inference/training requires significant RAM/VRAM for larger variants.
- `import_feasibility` is moderate (complex stack), so pin dependency versions for production.
- Gradio/Streamlit apps are good references, but MCP (Model Context Protocol) services should wrap backend functions directly for cleaner automation.
- DeepWiki analysis was unavailable; rely on repository source modules listed above.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/borisdayma/dalle-mini
- Main project README: `README.md`
- Docker notes: `Docker/README.md`
- Training script: `tools/train/train.py`
- Model core: `src/dalle_mini/model/modeling.py`
- Processor/config:
  - `src/dalle_mini/model/processor.py`
  - `src/dalle_mini/model/configuration.py`
- Inference backends:
  - `app/gradio/backend.py`
  - `app/streamlit/backend.py`