import os
import sys
from typing import Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import spacy
from spacy import explain
from spacy.cli.download import download as cli_download
from spacy.cli.train import train as cli_train
from spacy.cli.evaluate import evaluate as cli_evaluate
from spacy.cli.convert import convert as cli_convert
from spacy.cli.package import package as cli_package
from spacy.cli.debug_data import debug_data as cli_debug_data
from spacy.cli.debug_config import debug_config as cli_debug_config
from spacy.cli.debug_model import debug_model as cli_debug_model
from spacy.cli.init_config import init_config as cli_init_config
from spacy.cli.init_pipeline import init_pipeline as cli_init_pipeline
from spacy.cli.validate import validate as cli_validate
from spacy.cli.info import info as cli_info

mcp = FastMCP("spacy_service")


@mcp.tool(name="spacy_load_pipeline", description="Load a spaCy pipeline by model/package name.")
def spacy_load_pipeline(
    model_name: str,
    disable: Optional[list[str]] = None,
    enable: Optional[list[str]] = None,
    exclude: Optional[list[str]] = None,
) -> dict:
    """
    Load a spaCy pipeline.

    Parameters:
    - model_name: Model/package name (e.g. 'en_core_web_sm').
    - disable: Optional list of pipeline components to disable.
    - enable: Optional list of pipeline components to enable.
    - exclude: Optional list of pipeline components to exclude.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        nlp = spacy.load(model_name, disable=disable, enable=enable, exclude=exclude)
        return {"success": True, "result": {"pipe_names": nlp.pipe_names, "lang": nlp.lang}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_create_blank", description="Create a blank spaCy language pipeline.")
def spacy_create_blank(lang_code: str) -> dict:
    """
    Create a blank spaCy Language object.

    Parameters:
    - lang_code: Language code (e.g. 'en', 'de', 'fr').

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        nlp = spacy.blank(lang_code)
        return {"success": True, "result": {"lang": nlp.lang, "pipe_names": nlp.pipe_names}, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_process_text", description="Process text with a spaCy model and return basic annotations.")
def spacy_process_text(model_name: str, text: str) -> dict:
    """
    Run NLP processing and return token/sentence/entity summaries.

    Parameters:
    - model_name: Model/package name for loading pipeline.
    - text: Input text.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        nlp = spacy.load(model_name)
        doc = nlp(text)
        result = {
            "tokens": [t.text for t in doc],
            "sentences": [s.text for s in doc.sents] if doc.has_annotation("SENT_START") else [],
            "entities": [{"text": ent.text, "label": ent.label_} for ent in doc.ents],
        }
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_explain_label", description="Explain spaCy annotation labels and symbols.")
def spacy_explain_label(label: str) -> dict:
    """
    Explain a spaCy label/symbol (e.g. POS tags, dependency labels, entity tags).

    Parameters:
    - label: Label to explain.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        meaning = explain(label)
        return {"success": True, "result": meaning, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_download", description="Download a spaCy model package.")
def spacy_cli_download(model: str, direct: bool = False, sdist: bool = False) -> dict:
    """
    Download a spaCy model package.

    Parameters:
    - model: Model name.
    - direct: Whether to treat model argument as direct URL/package.
    - sdist: Whether to prefer source distribution.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_download(model, direct=direct, sdist=sdist)
        return {"success": True, "result": f"Downloaded model: {model}", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_train", description="Train a spaCy pipeline from config.")
def spacy_cli_train(config_path: str, output_path: str) -> dict:
    """
    Train a spaCy model from a config file.

    Parameters:
    - config_path: Path to training config file.
    - output_path: Output directory for trained pipeline.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_train(config_path, output_path=output_path)
        return {"success": True, "result": f"Training completed: {output_path}", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_evaluate", description="Evaluate a spaCy pipeline on a corpus.")
def spacy_cli_evaluate(model: str, data_path: str, output: Optional[str] = None) -> dict:
    """
    Evaluate a trained spaCy model.

    Parameters:
    - model: Trained model path/package.
    - data_path: Evaluation data path.
    - output: Optional output file for metrics.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        scores = cli_evaluate(model, data_path, output=output)
        return {"success": True, "result": scores, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_convert", description="Convert external data formats to spaCy training format.")
def spacy_cli_convert(
    input_path: str,
    output_dir: str,
    converter: str,
    n_sents: int = 10,
    merge_subtokens: bool = False,
) -> dict:
    """
    Convert annotation data into spaCy format.

    Parameters:
    - input_path: Input data file.
    - output_dir: Output directory.
    - converter: Converter name (e.g. 'conll', 'iob', 'json').
    - n_sents: Number of sentences per doc.
    - merge_subtokens: Merge subtokens.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_convert(
            input_path,
            output_dir,
            converter=converter,
            n_sents=n_sents,
            merge_subtokens=merge_subtokens,
        )
        return {"success": True, "result": f"Converted data to: {output_dir}", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_package", description="Package a trained spaCy pipeline as a Python package.")
def spacy_cli_package(input_dir: str, output_dir: str, name: str, version: str) -> dict:
    """
    Build a distributable package for a trained spaCy pipeline.

    Parameters:
    - input_dir: Trained pipeline directory.
    - output_dir: Build output directory.
    - name: Package name.
    - version: Package version.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_package(input_dir, output_dir, name=name, version=version)
        return {"success": True, "result": f"Packaged model to: {output_dir}", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_debug_data", description="Validate and inspect spaCy training/dev data.")
def spacy_cli_debug_data(config_path: str) -> dict:
    """
    Run spaCy debug-data checks.

    Parameters:
    - config_path: Path to config.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_debug_data(config_path)
        return {"success": True, "result": "debug-data completed", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_debug_config", description="Validate and inspect resolved spaCy config.")
def spacy_cli_debug_config(config_path: str) -> dict:
    """
    Run spaCy debug-config checks.

    Parameters:
    - config_path: Path to config.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_debug_config(config_path)
        return {"success": True, "result": "debug-config completed", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_debug_model", description="Inspect spaCy model architecture and behavior.")
def spacy_cli_debug_model(config_path: str) -> dict:
    """
    Run spaCy debug-model checks.

    Parameters:
    - config_path: Path to config.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_debug_model(config_path)
        return {"success": True, "result": "debug-model completed", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_init_config", description="Generate a starter spaCy training config.")
def spacy_cli_init_config(lang: str, pipeline: str, output_file: str) -> dict:
    """
    Initialize a spaCy config.

    Parameters:
    - lang: Language code.
    - pipeline: Comma-separated pipeline components.
    - output_file: Path to write config file.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_init_config(output_file, lang=lang, pipeline=pipeline.split(","))
        return {"success": True, "result": f"Config generated: {output_file}", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_init_pipeline", description="Initialize and scaffold a spaCy pipeline package.")
def spacy_cli_init_pipeline(lang: str, output_dir: str) -> dict:
    """
    Initialize pipeline scaffolding.

    Parameters:
    - lang: Language code.
    - output_dir: Output directory.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        cli_init_pipeline(lang=lang, output_dir=output_dir)
        return {"success": True, "result": f"Pipeline initialized: {output_dir}", "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_validate", description="Validate installed spaCy models and compatibility.")
def spacy_cli_validate() -> dict:
    """
    Validate spaCy installation and model compatibility.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        result = cli_validate()
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


@mcp.tool(name="spacy_cli_info", description="Show spaCy environment or model information.")
def spacy_cli_info(model: Optional[str] = None) -> dict:
    """
    Retrieve spaCy environment/model info.

    Parameters:
    - model: Optional model name/path.

    Returns:
    - Dictionary with success/result/error keys.
    """
    try:
        result = cli_info(model=model) if model else cli_info()
        return {"success": True, "result": result, "error": None}
    except Exception as e:
        return {"success": False, "result": None, "error": str(e)}


def create_app() -> FastMCP:
    return mcp