# dalle-mini MCP (Model Context Protocol) Service README

## 1) Project Introduction

This repository can be wrapped as an MCP (Model Context Protocol) service for text-to-image generation using the DALL·E Mini/BART-style model stack (JAX/Flax + Transformers).

Main capabilities:
- Generate images from text prompts
- Run local demo apps (Gradio/Streamlit backends)
- Train/fine-tune model variants via the training pipeline
- Reuse core modules for preprocessing, tokenization, and model inference

Core implementation lives in:
- `src/dalle_mini/` (model, config, processor, data pipeline)
- `app/gradio/` and `app/streamlit/` (inference app wrappers)
- `tools/train/train.py` (training entry script)

---

## 2) Installation Method

### Prerequisites
- Python 3.8+ (recommended: 3.9/3.10)
- pip
- JAX-compatible environment (CPU/GPU/TPU depending on your target)
- Enough RAM/VRAM for model loading and generation

### Install package
- `pip install -e .`

### Core dependencies (from repository analysis)
- Required: `jax`, `flax`, `transformers`, `numpy`, `Pillow`, `datasets`, `tokenizers`
- Optional: `gradio`, `streamlit`, `wandb`, TensorFlow ecosystem compatibility packages

If missing, install manually with pip in your environment.

---

## 3) Quick Start

### Run training
- `python tools/train/train.py`

Use JSON configs from:
- `tools/train/config/micro/config.json`
- `tools/train/config/mini/config.json`
- `tools/train/config/mini_glu/config.json`
- `tools/train/config/mega/config.json`

### Run local inference UIs
- Gradio: `python app/gradio/app.py`
- Streamlit: `python app/streamlit/app.py`

### Typical MCP (Model Context Protocol) service flow
1. Receive prompt from MCP (Model Context Protocol) client.
2. Normalize/process text (`model/text.py`, `model/processor.py`).
3. Run generation (`model/modeling.py`).
4. Return image artifact(s) or encoded image payload to client.

---

## 4) Available Tools and Endpoints List

Below is a practical endpoint mapping for an MCP (Model Context Protocol) service wrapper around this repo.

### `generate_image`
- Purpose: Generate image(s) from a text prompt
- Backed by: `dalle_mini.model.modeling`, processor + tokenizer utilities
- Input: prompt, generation params (seed, top_k/top_p, temperature, num_images)
- Output: image bytes/URLs/base64 metadata

### `batch_generate`
- Purpose: Generate images for multiple prompts in one request
- Backed by: same generation stack, batched preprocessing in data/model utilities
- Input: list of prompts + shared/per-item parameters
- Output: grouped generation results per prompt

### `health_check`
- Purpose: Service readiness/liveness verification
- Backed by: lightweight model/service state checks
- Output: status, model loaded flag, runtime info

### `train_model` (optional/admin)
- Purpose: Start or orchestrate training/fine-tuning jobs
- Backed by: `tools/train/train.py`
- Input: config path/overrides
- Output: run id, checkpoint/log locations, status

### `list_configs`
- Purpose: Show available built-in train configs
- Backed by: `tools/train/config/**`
- Output: config names/paths and brief descriptions

---

## 5) Common Issues and Notes

- JAX install mismatch: Ensure `jax`/`jaxlib` versions match your CUDA/CPU runtime.
- High memory usage: Generation/training can be heavy; start with smaller configs (`micro`/`mini`).
- Slow first request: Model initialization and JIT compilation can add startup latency.
- Optional UI deps missing: Install `gradio` or `streamlit` explicitly if app launch fails.
- Distributed training complexity: Partitioning logic (`model/partitions.py`) and optimizer settings require careful environment setup.
- No explicit console script entrypoint detected: run Python scripts directly as shown above.

---

## 6) Reference Links / Documentation

- Repository: https://github.com/borisdayma/dalle-mini
- Main project README: `README.md`
- Docker notes: `Docker/README.md`
- Training script: `tools/train/train.py`
- Model code: `src/dalle_mini/model/modeling.py`
- Data pipeline: `src/dalle_mini/data.py`
- Gradio app: `app/gradio/app.py`
- Streamlit app: `app/streamlit/app.py`

If you are packaging this as a production MCP (Model Context Protocol) service, add:
- request/response schema validation
- model warmup on startup
- concurrency limits and queueing
- observability (latency, GPU memory, error rates)
- artifact storage policy for generated images