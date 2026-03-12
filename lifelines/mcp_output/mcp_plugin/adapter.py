import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the lifelines repository.

    This adapter attempts to import and expose selected classes/functions discovered
    by repository analysis. It supports graceful fallback when imports fail and returns
    unified dictionary responses for every public method.
    """

    # -------------------------------------------------------------------------
    # Initialization and Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._symbols: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._initialize_imports()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "Success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if details:
            payload["details"] = details
        return payload

    def _initialize_imports(self) -> None:
        """
        Attempt to import all identified modules/symbols from analysis results.
        Uses full module paths (with source prefix removed due to sys.path setup).
        """
        targets = [
            ("conftest", "block"),
            ("docs.conftest", "tempdir"),
            ("docs.conf", "setup"),
            ("examples.crowther_royston_clements_splines", "generate_data"),
            ("examples.crowther_royston_clements_splines", "CRCSplineFitter"),
            ("examples.royston_parmar_splines", "PHSplineFitter"),
            ("examples.royston_parmar_splines", "POSplineFitter"),
            ("examples.royston_parmar_splines", "SplineFitter"),
            ("examples.cure_model", "CureModel"),
            ("examples.haft_model", "HAFT"),
            ("examples.copula_frailty_weibull_model", "CopulaFrailtyWeilbullModel"),
            ("examples.mixture_cure_model", "MixtureCureModel"),
        ]

        for module_path, symbol_name in targets:
            try:
                module = self._modules.get(module_path)
                if module is None:
                    module = importlib.import_module(module_path)
                    self._modules[module_path] = module
                symbol = getattr(module, symbol_name)
                self._symbols[f"{module_path}.{symbol_name}"] = symbol
            except Exception as e:
                self._import_errors[f"{module_path}.{symbol_name}"] = f"{type(e).__name__}: {e}"

    def health_check(self) -> Dict[str, Any]:
        """
        Report import availability and fallback readiness.

        Returns:
            Unified status dictionary with import summary and actionable guidance.
        """
        available = sorted(self._symbols.keys())
        failed = dict(self._import_errors)
        if failed:
            return self._ok(
                {
                    "available_symbols": available,
                    "failed_symbols": failed,
                    "fallback_ready": True,
                },
                message="Partial import success. Fallback mode is available for missing symbols.",
            )
        return self._ok(
            {
                "available_symbols": available,
                "failed_symbols": {},
                "fallback_ready": True,
            },
            message="All identified symbols imported successfully.",
        )

    def _resolve_symbol(self, module_path: str, symbol_name: str) -> Tuple[Optional[Any], Optional[Dict[str, Any]]]:
        key = f"{module_path}.{symbol_name}"
        symbol = self._symbols.get(key)
        if symbol is not None:
            return symbol, None
        err = self._import_errors.get(key, "Unknown import issue.")
        return None, self._err(
            message=f"Requested symbol is unavailable: {key}",
            guidance=(
                "Verify repository source is present under the expected 'source' directory, "
                "install required dependencies (numpy, scipy, pandas, matplotlib, autograd, "
                "autograd-gamma, formulaic), and retry health_check()."
            ),
            details=err,
        )

    def _instantiate(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        cls, err = self._resolve_symbol(module_path, class_name)
        if err:
            return err
        try:
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance, "class": f"{module_path}.{class_name}"}, message="Instance created.")
        except Exception as e:
            return self._err(
                message=f"Failed to instantiate class: {module_path}.{class_name}",
                guidance="Check constructor arguments and dependency availability.",
                details=f"{type(e).__name__}: {e}",
            )

    def _call(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        fn, err = self._resolve_symbol(module_path, function_name)
        if err:
            return err
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result, "function": f"{module_path}.{function_name}"}, message="Function executed.")
        except Exception as e:
            return self._err(
                message=f"Failed to execute function: {module_path}.{function_name}",
                guidance="Review function parameters and input data shapes/types.",
                details=f"{type(e).__name__}: {e}",
            )

    # -------------------------------------------------------------------------
    # Functions from discovered modules
    # -------------------------------------------------------------------------
    def call_conftest_block(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call conftest.block(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to conftest.block.
            **kwargs: Keyword arguments forwarded to conftest.block.

        Returns:
            Unified status dictionary with function result or actionable error.
        """
        return self._call("conftest", "block", *args, **kwargs)

    def call_docs_conftest_tempdir(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call docs.conftest.tempdir(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to docs.conftest.tempdir.
            **kwargs: Keyword arguments forwarded to docs.conftest.tempdir.

        Returns:
            Unified status dictionary with function result or actionable error.
        """
        return self._call("docs.conftest", "tempdir", *args, **kwargs)

    def call_docs_conf_setup(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call docs.conf.setup(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to docs.conf.setup.
            **kwargs: Keyword arguments forwarded to docs.conf.setup.

        Returns:
            Unified status dictionary with function result or actionable error.
        """
        return self._call("docs.conf", "setup", *args, **kwargs)

    def call_generate_data(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call examples.crowther_royston_clements_splines.generate_data(*args, **kwargs).

        Parameters:
            *args: Positional arguments forwarded to generate_data.
            **kwargs: Keyword arguments forwarded to generate_data.

        Returns:
            Unified status dictionary with generated data or actionable error.
        """
        return self._call("examples.crowther_royston_clements_splines", "generate_data", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Class instance factory methods
    # -------------------------------------------------------------------------
    def create_crc_spline_fitter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.crowther_royston_clements_splines.CRCSplineFitter.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.crowther_royston_clements_splines", "CRCSplineFitter", *args, **kwargs)

    def create_ph_spline_fitter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.royston_parmar_splines.PHSplineFitter.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.royston_parmar_splines", "PHSplineFitter", *args, **kwargs)

    def create_po_spline_fitter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.royston_parmar_splines.POSplineFitter.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.royston_parmar_splines", "POSplineFitter", *args, **kwargs)

    def create_spline_fitter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.royston_parmar_splines.SplineFitter.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.royston_parmar_splines", "SplineFitter", *args, **kwargs)

    def create_cure_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.cure_model.CureModel.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.cure_model", "CureModel", *args, **kwargs)

    def create_haft_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.haft_model.HAFT.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.haft_model", "HAFT", *args, **kwargs)

    def create_copula_frailty_weilbull_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.copula_frailty_weibull_model.CopulaFrailtyWeilbullModel.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate(
            "examples.copula_frailty_weibull_model",
            "CopulaFrailtyWeilbullModel",
            *args,
            **kwargs,
        )

    def create_mixture_cure_model(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.mixture_cure_model.MixtureCureModel.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Unified status dictionary containing created instance or actionable error.
        """
        return self._instantiate("examples.mixture_cure_model", "MixtureCureModel", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Utility for runtime troubleshooting
    # -------------------------------------------------------------------------
    def debug_trace(self, exc: BaseException) -> Dict[str, Any]:
        """
        Return a structured traceback payload for debugging adapter-level exceptions.

        Parameters:
            exc: Exception object to format.

        Returns:
            Unified error dictionary with traceback details.
        """
        return self._err(
            message="Adapter debug trace generated.",
            guidance="Inspect details and fix module paths, missing dependencies, or invalid inputs.",
            details="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
        )