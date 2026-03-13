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

from phonopy.scripts import (
    phonopy as phonopy_cli,
    phonopy_bandplot,
    phonopy_calc_convert,
    phonopy_gruneisen,
    phonopy_gruneisenplot,
    phonopy_load,
    phonopy_pdosplot,
    phonopy_propplot,
    phonopy_qe_born,
    phonopy_qha,
    phonopy_tdplot,
    phonopy_vasp_born,
    phonopy_vasp_efe,
)

mcp = FastMCP("phonopy_mcp_service")


def _run_cli_main(module: Any, argv: list[str]) -> dict:
    try:
        old_argv = sys.argv[:]
        sys.argv = argv[:]
        module.main()
        return {"success": True, "result": "completed", "error": None}
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 0
        if code == 0:
            return {"success": True, "result": "completed", "error": None}
        return {"success": False, "result": None, "error": f"Exited with code {code}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}
    finally:
        sys.argv = old_argv


@mcp.tool(name="phonopy_run", description="Run the main phonopy CLI workflow with explicit arguments.")
def phonopy_run(args: list[str]) -> dict:
    """
    Run the primary phonopy command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Dict with keys:
      - success: bool indicating execution success.
      - result: execution result string on success.
      - error: error message on failure, otherwise None.
    """
    return _run_cli_main(phonopy_cli, ["phonopy"] + args)


@mcp.tool(name="phonopy_load_run", description="Run phonopy-load to load and process existing phonopy data.")
def phonopy_load_run(args: list[str]) -> dict:
    """
    Execute phonopy-load command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_load, ["phonopy-load"] + args)


@mcp.tool(name="phonopy_bandplot_run", description="Run phonopy-bandplot for band structure plotting.")
def phonopy_bandplot_run(args: list[str]) -> dict:
    """
    Execute phonopy-bandplot command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_bandplot, ["phonopy-bandplot"] + args)


@mcp.tool(name="phonopy_gruneisen_run", description="Run phonopy-gruneisen for Gruneisen workflows.")
def phonopy_gruneisen_run(args: list[str]) -> dict:
    """
    Execute phonopy-gruneisen command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_gruneisen, ["phonopy-gruneisen"] + args)


@mcp.tool(name="phonopy_gruneisenplot_run", description="Run phonopy-gruneisenplot to plot Gruneisen outputs.")
def phonopy_gruneisenplot_run(args: list[str]) -> dict:
    """
    Execute phonopy-gruneisenplot command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_gruneisenplot, ["phonopy-gruneisenplot"] + args)


@mcp.tool(name="phonopy_qha_run", description="Run phonopy-qha for quasi-harmonic approximation analysis.")
def phonopy_qha_run(args: list[str]) -> dict:
    """
    Execute phonopy-qha command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_qha, ["phonopy-qha"] + args)


@mcp.tool(name="phonopy_pdosplot_run", description="Run phonopy-pdosplot for projected DOS plotting.")
def phonopy_pdosplot_run(args: list[str]) -> dict:
    """
    Execute phonopy-pdosplot command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_pdosplot, ["phonopy-pdosplot"] + args)


@mcp.tool(name="phonopy_propplot_run", description="Run phonopy-propplot for thermal property plotting.")
def phonopy_propplot_run(args: list[str]) -> dict:
    """
    Execute phonopy-propplot command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_propplot, ["phonopy-propplot"] + args)


@mcp.tool(name="phonopy_tdplot_run", description="Run phonopy-tdplot for thermal displacement plotting.")
def phonopy_tdplot_run(args: list[str]) -> dict:
    """
    Execute phonopy-tdplot command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_tdplot, ["phonopy-tdplot"] + args)


@mcp.tool(name="phonopy_calc_convert_run", description="Run phonopy-calc-convert for calculator-format conversion.")
def phonopy_calc_convert_run(args: list[str]) -> dict:
    """
    Execute phonopy-calc-convert command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_calc_convert, ["phonopy-calc-convert"] + args)


@mcp.tool(name="phonopy_qe_born_run", description="Run phonopy-qe-born for Quantum ESPRESSO Born charge workflows.")
def phonopy_qe_born_run(args: list[str]) -> dict:
    """
    Execute phonopy-qe-born command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_qe_born, ["phonopy-qe-born"] + args)


@mcp.tool(name="phonopy_vasp_born_run", description="Run phonopy-vasp-born for VASP Born charge workflows.")
def phonopy_vasp_born_run(args: list[str]) -> dict:
    """
    Execute phonopy-vasp-born command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_vasp_born, ["phonopy-vasp-born"] + args)


@mcp.tool(name="phonopy_vasp_efe_run", description="Run phonopy-vasp-efe for VASP EFE helper workflow.")
def phonopy_vasp_efe_run(args: list[str]) -> dict:
    """
    Execute phonopy-vasp-efe command.

    Parameters:
    - args: List of command-line arguments excluding executable name.

    Returns:
    - Standard result dictionary with success/result/error.
    """
    return _run_cli_main(phonopy_vasp_efe, ["phonopy-vasp-efe"] + args)


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()