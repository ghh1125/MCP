import os
import sys

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)

from typing import Any, Dict, Optional


class Adapter:
    """
    MCP Import Mode Adapter for the VULCAN repository.

    This adapter attempts to import and expose key classes/functions discovered in analysis:
    - store: AtmData, Parameters, Variables
    - build_atm: Atm, InitialAbun
    - op: Integration, ODESolver, Output
    - chem_funs: Gibbs
    - make_chem_funs: check_conserv, check_duplicate, make_Gibbs

    It provides:
    - Import-mode execution with graceful fallback hints
    - Unified return schema with a mandatory `status` field
    - Structured module management and robust error handling
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Module Loading
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt to load repository modules.

        Returns:
            None
        """
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._load_error: Optional[str] = None
        self._load_modules()

    def _result(
        self,
        status: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        result = {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data or {},
        }
        if guidance:
            result["guidance"] = guidance
        return result

    def _load_modules(self) -> None:
        """
        Attempt to import all required modules and symbols from the local source tree.
        """
        try:
            import store as store_module
            import build_atm as build_atm_module
            import op as op_module
            import chem_funs as chem_funs_module
            import make_chem_funs as make_chem_funs_module

            self._modules["store"] = store_module
            self._modules["build_atm"] = build_atm_module
            self._modules["op"] = op_module
            self._modules["chem_funs"] = chem_funs_module
            self._modules["make_chem_funs"] = make_chem_funs_module

            self._symbols["AtmData"] = getattr(store_module, "AtmData", None)
            self._symbols["Parameters"] = getattr(store_module, "Parameters", None)
            self._symbols["Variables"] = getattr(store_module, "Variables", None)

            self._symbols["Atm"] = getattr(build_atm_module, "Atm", None)
            self._symbols["InitialAbun"] = getattr(build_atm_module, "InitialAbun", None)

            self._symbols["Integration"] = getattr(op_module, "Integration", None)
            self._symbols["ODESolver"] = getattr(op_module, "ODESolver", None)
            self._symbols["Output"] = getattr(op_module, "Output", None)

            self._symbols["Gibbs"] = getattr(chem_funs_module, "Gibbs", None)

            self._symbols["check_conserv"] = getattr(make_chem_funs_module, "check_conserv", None)
            self._symbols["check_duplicate"] = getattr(make_chem_funs_module, "check_duplicate", None)
            self._symbols["make_Gibbs"] = getattr(make_chem_funs_module, "make_Gibbs", None)

        except Exception as exc:
            self._load_error = str(exc)

    def health(self) -> Dict[str, Any]:
        """
        Return adapter import health and availability of discovered symbols.

        Returns:
            Dict[str, Any]: Unified result dictionary with symbol availability.
        """
        symbol_state = {k: (v is not None) for k, v in self._symbols.items()}
        if self._load_error:
            return self._result(
                status="error",
                message="Import mode initialization failed.",
                data={"symbols": symbol_state, "error": self._load_error},
                guidance=(
                    "Ensure repository source files are present under the expected source path. "
                    "If import mode is unavailable, run CLI entry points such as: "
                    "`python vulcan.py`, `python build_atm.py`, or `python make_chem_funs.py`."
                ),
            )
        return self._result(
            status="success",
            message="Import mode is ready.",
            data={"symbols": symbol_state},
        )

    # -------------------------------------------------------------------------
    # Utility
    # -------------------------------------------------------------------------

    def _instantiate(self, symbol_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        cls = self._symbols.get(symbol_name)
        if cls is None:
            return self._result(
                status="error",
                message=f"Requested class '{symbol_name}' is not available.",
                guidance="Verify module import success with `health()` and confirm repository integrity.",
            )
        try:
            instance = cls(*args, **kwargs)
            return self._result(
                status="success",
                message=f"Instance of '{symbol_name}' created successfully.",
                data={"class": symbol_name, "instance": instance},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Failed to instantiate '{symbol_name}': {exc}",
                guidance="Check constructor parameters and required runtime configuration/files.",
            )

    def _call(self, symbol_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn = self._symbols.get(symbol_name)
        if fn is None:
            return self._result(
                status="error",
                message=f"Requested function '{symbol_name}' is not available.",
                guidance="Verify module import success with `health()` and ensure function exists in source.",
            )
        try:
            output = fn(*args, **kwargs)
            return self._result(
                status="success",
                message=f"Function '{symbol_name}' executed successfully.",
                data={"function": symbol_name, "result": output},
            )
        except Exception as exc:
            return self._result(
                status="error",
                message=f"Function '{symbol_name}' execution failed: {exc}",
                guidance="Validate input arguments and dependent data files expected by VULCAN.",
            )

    # -------------------------------------------------------------------------
    # store module: class factories
    # -------------------------------------------------------------------------

    def create_atmdata(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of store.AtmData.

        Parameters:
            *args: Positional arguments forwarded to AtmData constructor.
            **kwargs: Keyword arguments forwarded to AtmData constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("AtmData", *args, **kwargs)

    def create_parameters(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of store.Parameters.

        Parameters:
            *args: Positional arguments forwarded to Parameters constructor.
            **kwargs: Keyword arguments forwarded to Parameters constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("Parameters", *args, **kwargs)

    def create_variables(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of store.Variables.

        Parameters:
            *args: Positional arguments forwarded to Variables constructor.
            **kwargs: Keyword arguments forwarded to Variables constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("Variables", *args, **kwargs)

    # -------------------------------------------------------------------------
    # build_atm module: class factories
    # -------------------------------------------------------------------------

    def create_atm(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of build_atm.Atm.

        Parameters:
            *args: Positional arguments forwarded to Atm constructor.
            **kwargs: Keyword arguments forwarded to Atm constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("Atm", *args, **kwargs)

    def create_initial_abun(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of build_atm.InitialAbun.

        Parameters:
            *args: Positional arguments forwarded to InitialAbun constructor.
            **kwargs: Keyword arguments forwarded to InitialAbun constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("InitialAbun", *args, **kwargs)

    # -------------------------------------------------------------------------
    # op module: class factories
    # -------------------------------------------------------------------------

    def create_integration(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of op.Integration.

        Parameters:
            *args: Positional arguments forwarded to Integration constructor.
            **kwargs: Keyword arguments forwarded to Integration constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("Integration", *args, **kwargs)

    def create_odesolver(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of op.ODESolver.

        Parameters:
            *args: Positional arguments forwarded to ODESolver constructor.
            **kwargs: Keyword arguments forwarded to ODESolver constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("ODESolver", *args, **kwargs)

    def create_output(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of op.Output.

        Parameters:
            *args: Positional arguments forwarded to Output constructor.
            **kwargs: Keyword arguments forwarded to Output constructor.

        Returns:
            Dict[str, Any]: Unified status result with created instance or actionable error.
        """
        return self._instantiate("Output", *args, **kwargs)

    # -------------------------------------------------------------------------
    # chem_funs module: function calls
    # -------------------------------------------------------------------------

    def call_gibbs(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute chem_funs.Gibbs.

        Parameters:
            *args: Positional arguments for Gibbs.
            **kwargs: Keyword arguments for Gibbs.

        Returns:
            Dict[str, Any]: Unified status result with function output or actionable error.
        """
        return self._call("Gibbs", *args, **kwargs)

    # -------------------------------------------------------------------------
    # make_chem_funs module: function calls
    # -------------------------------------------------------------------------

    def call_check_conserv(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute make_chem_funs.check_conserv.

        Parameters:
            *args: Positional arguments for check_conserv.
            **kwargs: Keyword arguments for check_conserv.

        Returns:
            Dict[str, Any]: Unified status result with function output or actionable error.
        """
        return self._call("check_conserv", *args, **kwargs)

    def call_check_duplicate(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute make_chem_funs.check_duplicate.

        Parameters:
            *args: Positional arguments for check_duplicate.
            **kwargs: Keyword arguments for check_duplicate.

        Returns:
            Dict[str, Any]: Unified status result with function output or actionable error.
        """
        return self._call("check_duplicate", *args, **kwargs)

    def call_make_gibbs(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Execute make_chem_funs.make_Gibbs.

        Parameters:
            *args: Positional arguments for make_Gibbs.
            **kwargs: Keyword arguments for make_Gibbs.

        Returns:
            Dict[str, Any]: Unified status result with function output or actionable error.
        """
        return self._call("make_Gibbs", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Fallback / Guidance
    # -------------------------------------------------------------------------

    def fallback_cli_guidance(self) -> Dict[str, Any]:
        """
        Provide CLI fallback guidance when import mode is partially/fully unavailable.

        Returns:
            Dict[str, Any]: Unified status result with actionable CLI alternatives.
        """
        return self._result(
            status="success",
            message="CLI fallback guidance is available.",
            data={
                "commands": [
                    "python vulcan.py",
                    "python build_atm.py",
                    "python make_chem_funs.py",
                    "python tools/make_mix_table.py",
                    "python tools/print_actinic_flux.py",
                ],
                "note": (
                    "Use these commands when direct imports fail due to runtime coupling, "
                    "missing data paths, or environment-specific assumptions."
                ),
            },
        )