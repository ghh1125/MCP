import os
import sys
from typing import Any

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)

from fastmcp import FastMCP
import monai


mcp = FastMCP("monai_service")


def _ok(result: Any) -> dict:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> dict:
    return {"success": False, "result": None, "error": message}


@mcp.tool(name="monai_version", description="Get MONAI version and basic environment info.")
def monai_version() -> dict:
    """
    Return MONAI version details.

    Returns:
        dict: Standard response dictionary with version and module path details.
    """
    try:
        result = {
            "version": getattr(monai, "__version__", "unknown"),
            "module": monai.__name__,
            "file": getattr(monai, "__file__", None),
        }
        return _ok(result)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="bundle_run", description="Run MONAI bundle CLI-style commands programmatically.")
def bundle_run(args: str) -> dict:
    """
    Execute MONAI bundle script entry with argument string.

    Parameters:
        args (str): CLI-like argument string, e.g. 'run --config_file config.json'.

    Returns:
        dict: Standard response dictionary with script return value.
    """
    try:
        from monai.bundle.scripts import run as bundle_run_fn

        argv = [a for a in args.split(" ") if a.strip()]
        out = bundle_run_fn(argv)
        return _ok(out)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="auto3dseg_run", description="Run Auto3DSeg pipeline from MONAI apps.")
def auto3dseg_run(
    input_data_config: str,
    work_dir: str,
    algorithms: str = "",
    templates_path_or_url: str = "",
) -> dict:
    """
    Launch an Auto3DSeg run using MONAI AutoRunner.

    Parameters:
        input_data_config (str): Path to data list/config JSON.
        work_dir (str): Working directory for outputs.
        algorithms (str): Comma-separated algorithm names to include.
        templates_path_or_url (str): Optional local path or URL for templates.

    Returns:
        dict: Standard response dictionary with run status/output.
    """
    try:
        from monai.apps.auto3dseg.auto_runner import AutoRunner

        algos = [a.strip() for a in algorithms.split(",") if a.strip()] or None
        runner = AutoRunner(
            input=input_data_config,
            work_dir=work_dir,
            algos=algos,
            templates_path_or_url=templates_path_or_url or None,
        )
        output = runner.run()
        return _ok(output)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="nnunetv2_run", description="Run MONAI nnUNetV2 workflow wrapper.")
def nnunetv2_run(
    input_config: str,
    work_dir: str,
    datalist: str = "",
    fold: int = 0,
) -> dict:
    """
    Execute nnUNetV2 runner from MONAI apps.

    Parameters:
        input_config (str): Path to nnUNetV2 config file.
        work_dir (str): Working directory.
        datalist (str): Optional datalist path.
        fold (int): Fold index.

    Returns:
        dict: Standard response dictionary with runner output.
    """
    try:
        from monai.apps.nnunet.nnunetv2_runner import NNUNetV2Runner

        runner = NNUNetV2Runner(
            input_config=input_config,
            work_dir=work_dir,
            datalist=datalist or None,
            fold=fold,
        )
        output = runner.run()
        return _ok(output)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="config_parse", description="Parse a MONAI bundle config file and return resolved content.")
def config_parse(config_file: str) -> dict:
    """
    Parse and resolve MONAI bundle configuration.

    Parameters:
        config_file (str): Path to config JSON/YAML.

    Returns:
        dict: Standard response dictionary with parsed config content.
    """
    try:
        from monai.bundle.config_parser import ConfigParser

        parser = ConfigParser()
        parser.read_config(config_file)
        parser.parse()
        content = parser.get_parsed_content()
        return _ok(content)
    except Exception as exc:
        return _err(str(exc))


@mcp.tool(name="list_optional_dependencies", description="Check presence of common optional MONAI dependencies.")
def list_optional_dependencies() -> dict:
    """
    Check import availability for key optional packages used by MONAI.

    Returns:
        dict: Standard response dictionary containing package availability map.
    """
    try:
        packages = [
            "nibabel",
            "SimpleITK",
            "pydicom",
            "itk",
            "scipy",
            "PIL",
            "ignite",
            "einops",
            "skimage",
            "mlflow",
            "tensorboard",
            "cv2",
            "cucim",
            "zarr",
        ]
        availability = {}
        for pkg in packages:
            try:
                __import__(pkg)
                availability[pkg] = True
            except Exception:
                availability[pkg] = False
        return _ok(availability)
    except Exception as exc:
        return _err(str(exc))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()