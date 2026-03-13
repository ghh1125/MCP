import os
import sys
from typing import Dict, Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP

mcp = FastMCP("dalle_mini_service")


def _safe_import(module_name: str):
    try:
        module = __import__(module_name, fromlist=["*"])
        return module, None
    except Exception as exc:
        return None, str(exc)


@mcp.tool(
    name="generate_images_gradio_backend",
    description="Generate images from text prompt using Gradio backend predictor.",
)
def generate_images_gradio_backend(prompt: str, seed: int = 0, top_k: int = 256, top_p: float = 0.95) -> Dict[str, Any]:
    """
    Generate images from a text prompt via app.gradio.backend if available.

    Parameters:
        prompt: Text prompt to render.
        seed: Random seed for reproducibility.
        top_k: Top-k sampling parameter.
        top_p: Top-p sampling parameter.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        backend, err = _safe_import("app.gradio.backend")
        if backend is None:
            return {"success": False, "result": None, "error": err}

        predict_fn = getattr(backend, "predict", None)
        if predict_fn is None:
            return {"success": False, "result": None, "error": "predict function not found in app.gradio.backend"}

        output = predict_fn(prompt, seed=seed, top_k=top_k, top_p=top_p)
        return {"success": True, "result": output, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="generate_images_streamlit_backend",
    description="Generate images from text prompt using Streamlit backend predictor.",
)
def generate_images_streamlit_backend(prompt: str, seed: int = 0, top_k: int = 256, top_p: float = 0.95) -> Dict[str, Any]:
    """
    Generate images from a text prompt via app.streamlit.backend if available.

    Parameters:
        prompt: Text prompt to render.
        seed: Random seed for reproducibility.
        top_k: Top-k sampling parameter.
        top_p: Top-p sampling parameter.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        backend, err = _safe_import("app.streamlit.backend")
        if backend is None:
            return {"success": False, "result": None, "error": err}

        predict_fn = getattr(backend, "predict", None)
        if predict_fn is None:
            return {"success": False, "result": None, "error": "predict function not found in app.streamlit.backend"}

        output = predict_fn(prompt, seed=seed, top_k=top_k, top_p=top_p)
        return {"success": True, "result": output, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="tokenize_text",
    description="Tokenize text using dalle_mini model tokenizer utilities.",
)
def tokenize_text(text: str) -> Dict[str, Any]:
    """
    Tokenize input text with dalle_mini tokenizer module if available.

    Parameters:
        text: Input text to tokenize.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        tokenizer_mod, err = _safe_import("src.dalle_mini.model.tokenizer")
        if tokenizer_mod is None:
            tokenizer_mod, err = _safe_import("dalle_mini.model.tokenizer")
        if tokenizer_mod is None:
            return {"success": False, "result": None, "error": err}

        tokenizer_cls = getattr(tokenizer_mod, "DalleBartTokenizer", None)
        if tokenizer_cls is None:
            return {"success": False, "result": None, "error": "DalleBartTokenizer not found"}

        tokenizer = tokenizer_cls.from_pretrained("dalle-mini/dalle-mini")
        tokens = tokenizer(text)
        return {"success": True, "result": tokens, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="load_model_config",
    description="Load DALLE Mini model configuration from local module.",
)
def load_model_config() -> Dict[str, Any]:
    """
    Load available model config classes from dalle_mini.model.configuration.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        cfg_mod, err = _safe_import("src.dalle_mini.model.configuration")
        if cfg_mod is None:
            cfg_mod, err = _safe_import("dalle_mini.model.configuration")
        if cfg_mod is None:
            return {"success": False, "result": None, "error": err}

        exported = [name for name in dir(cfg_mod) if name.lower().endswith("config")]
        return {"success": True, "result": exported, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="inspect_modeling_symbols",
    description="Inspect key symbols exposed by dalle_mini.model.modeling.",
)
def inspect_modeling_symbols(limit: int = 50) -> Dict[str, Any]:
    """
    List non-private symbols from the modeling module.

    Parameters:
        limit: Maximum number of symbols to return.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        modeling_mod, err = _safe_import("src.dalle_mini.model.modeling")
        if modeling_mod is None:
            modeling_mod, err = _safe_import("dalle_mini.model.modeling")
        if modeling_mod is None:
            return {"success": False, "result": None, "error": err}

        symbols = [name for name in dir(modeling_mod) if not name.startswith("_")]
        return {"success": True, "result": symbols[:limit], "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(
    name="run_training_entrypoint",
    description="Invoke training script main entrypoint with explicit arguments.",
)
def run_training_entrypoint(
    output_dir: str,
    dataset_repo_or_path: str,
    model_config_name: str = "mini",
    epochs: int = 1,
) -> Dict[str, Any]:
    """
    Attempt to run tools.train.train main-style routine with controlled parameters.

    Parameters:
        output_dir: Directory to store checkpoints/artifacts.
        dataset_repo_or_path: Dataset identifier/path for training.
        model_config_name: Training config preset name.
        epochs: Number of epochs.

    Returns:
        Dict with success/result/error fields.
    """
    try:
        train_mod, err = _safe_import("tools.train.train")
        if train_mod is None:
            return {"success": False, "result": None, "error": err}

        main_fn = getattr(train_mod, "main", None)
        if main_fn is None:
            return {"success": False, "result": None, "error": "main function not found in tools.train.train"}

        argv_backup = list(sys.argv)
        sys.argv = [
            "train.py",
            "--output_dir",
            output_dir,
            "--dataset_repo_or_path",
            dataset_repo_or_path,
            "--config_name",
            model_config_name,
            "--num_train_epochs",
            str(epochs),
        ]
        try:
            result = main_fn()
        finally:
            sys.argv = argv_backup

        return {"success": True, "result": result, "error": None}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()