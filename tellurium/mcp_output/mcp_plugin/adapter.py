import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the Tellurium repository.

    This adapter attempts to import and call functionality from:
      - tellurium package root
      - tellurium.tellurium module
      - selected utility/analysis/plotting modules

    All methods return a unified dictionary:
      {
        "status": "success" | "error" | "fallback",
        ...
      }
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}

        self._targets = {
            "tellurium_pkg": "tellurium",
            "tellurium_core": "tellurium.tellurium",
            "teconverters_inline_omex": "tellurium.teconverters.inline_omex",
            "teconverters_convert_omex": "tellurium.teconverters.convert_omex",
            "teconverters_convert_antimony": "tellurium.teconverters.convert_antimony",
            "teconverters_convert_phrasedml": "tellurium.teconverters.convert_phrasedml",
            "analysis_parameterscan": "tellurium.analysis.parameterscan",
            "analysis_bifurcation": "tellurium.analysis.bifurcation",
            "plotting_api": "tellurium.plotting.api",
            "utils_omex": "tellurium.utils.omex",
            "utils_misc": "tellurium.utils.misc",
        }

        self._initialize_imports()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _initialize_imports(self) -> None:
        for key, mod_path in self._targets.items():
            try:
                self._modules[key] = importlib.import_module(mod_path)
            except Exception as exc:
                self._modules[key] = None
                self._import_errors[key] = (
                    f"Failed to import '{mod_path}'. "
                    f"Please verify local source availability and dependencies. Details: {exc}"
                )

    def _result_success(self, **payload: Any) -> Dict[str, Any]:
        out = {"status": "success"}
        out.update(payload)
        return out

    def _result_error(self, message: str, **payload: Any) -> Dict[str, Any]:
        out = {"status": "error", "error": message}
        out.update(payload)
        return out

    def _result_fallback(self, message: str, **payload: Any) -> Dict[str, Any]:
        out = {"status": "fallback", "message": message}
        out.update(payload)
        return out

    def _get_module(self, key: str) -> Optional[Any]:
        return self._modules.get(key)

    def _safe_call(self, fn: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        try:
            value = fn(*args, **kwargs)
            return self._result_success(result=value)
        except Exception as exc:
            return self._result_error(
                "Function call failed. Check arguments and model format.",
                details=str(exc),
                traceback=traceback.format_exc(),
            )

    def _call_attr(self, module_key: str, attr_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod = self._get_module(module_key)
        if mod is None:
            return self._result_fallback(
                f"Module '{self._targets[module_key]}' is unavailable.",
                import_error=self._import_errors.get(module_key),
            )
        fn = getattr(mod, attr_name, None)
        if fn is None:
            return self._result_error(
                f"Attribute '{attr_name}' not found in module '{self._targets[module_key]}'.",
                guidance="Verify repository version and function availability.",
            )
        return self._safe_call(fn, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Report import health for all tracked modules.

        Returns:
            dict: status plus imported/unavailable module sets and error details.
        """
        imported = [k for k, v in self._modules.items() if v is not None]
        unavailable = [k for k, v in self._modules.items() if v is None]
        return self._result_success(
            mode=self.mode,
            imported_modules=imported,
            unavailable_modules=unavailable,
            import_errors=self._import_errors,
        )

    # -------------------------------------------------------------------------
    # tellurium root functions (high-value API surface)
    # -------------------------------------------------------------------------
    def call_loada(self, antimony_str: str) -> Dict[str, Any]:
        """
        Load an Antimony model string into a simulation object.

        Args:
            antimony_str: Antimony model text.

        Returns:
            dict: unified status/result.
        """
        return self._call_attr("tellurium_pkg", "loada", antimony_str)

    def call_loadsbml(self, sbml_str: str) -> Dict[str, Any]:
        """
        Load an SBML model string into a simulation object.

        Args:
            sbml_str: SBML XML text.

        Returns:
            dict: unified status/result.
        """
        return self._call_attr("tellurium_pkg", "loadSBMLModel", sbml_str)

    def call_load_model(self, model_source: str) -> Dict[str, Any]:
        """
        Generic model load entrypoint where available.

        Args:
            model_source: Input string/path for model loading.

        Returns:
            dict: unified status/result.
        """
        res = self._call_attr("tellurium_pkg", "loadModel", model_source)
        if res["status"] == "error":
            return self._call_attr("tellurium_pkg", "loada", model_source)
        return res

    def call_antimony_to_sbml(self, antimony_str: str) -> Dict[str, Any]:
        """
        Convert Antimony text to SBML when converter is available.

        Args:
            antimony_str: Antimony model text.

        Returns:
            dict: unified status/result.
        """
        return self._call_attr("tellurium_pkg", "antimonyToSBML", antimony_str)

    def call_sbml_to_antimony(self, sbml_str: str) -> Dict[str, Any]:
        """
        Convert SBML text to Antimony when converter is available.

        Args:
            sbml_str: SBML XML text.

        Returns:
            dict: unified status/result.
        """
        return self._call_attr("tellurium_pkg", "sbmlToAntimony", sbml_str)

    def call_execute_inline_omex(self, inline_omex: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute an inline OMEX specification.

        Args:
            inline_omex: Inline OMEX content.
            working_dir: Optional working directory.

        Returns:
            dict: unified status/result.
        """
        kwargs = {}
        if working_dir is not None:
            kwargs["workingDir"] = working_dir
        return self._call_attr("tellurium_pkg", "executeInlineOmex", inline_omex, **kwargs)

    # -------------------------------------------------------------------------
    # teconverters modules
    # -------------------------------------------------------------------------
    def call_inline_omex_to_omex(self, inline_omex_str: str, out_path: str) -> Dict[str, Any]:
        """
        Convert inline OMEX text to a COMBINE archive via teconverters if available.

        Args:
            inline_omex_str: Inline OMEX string content.
            out_path: Output OMEX archive path.

        Returns:
            dict: unified status/result.
        """
        mod = self._get_module("teconverters_inline_omex")
        if mod is None:
            return self._result_fallback(
                "Inline OMEX converter module unavailable.",
                import_error=self._import_errors.get("teconverters_inline_omex"),
            )

        candidate_names = ["saveInlineOMEX", "inlineOmexToCombineArchive", "convertInlineOmexToOmex"]
        for name in candidate_names:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, inline_omex_str, out_path)

        return self._result_error(
            "No known inline OMEX conversion function found.",
            guidance="Inspect tellurium.teconverters.inline_omex for available API names.",
        )

    # -------------------------------------------------------------------------
    # analysis helpers
    # -------------------------------------------------------------------------
    def create_parameter_scan_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance from tellurium.analysis.parameterscan classes.

        This method tries known class names used by Tellurium parameter scan APIs.

        Returns:
            dict: unified status/result containing instantiated object.
        """
        mod = self._get_module("analysis_parameterscan")
        if mod is None:
            return self._result_fallback(
                "Parameter scan module unavailable.",
                import_error=self._import_errors.get("analysis_parameterscan"),
            )

        for class_name in ["ParameterScan", "SteadyStateScan", "ParameterScan2D"]:
            cls = getattr(mod, class_name, None)
            if isinstance(cls, type):
                try:
                    instance = cls(*args, **kwargs)
                    return self._result_success(class_name=class_name, instance=instance)
                except Exception:
                    continue

        return self._result_error(
            "Could not instantiate a known parameter scan class.",
            guidance="Provide constructor arguments matching Tellurium version in source.",
        )

    def create_bifurcation_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a bifurcation analysis class instance if present.

        Returns:
            dict: unified status/result.
        """
        mod = self._get_module("analysis_bifurcation")
        if mod is None:
            return self._result_fallback(
                "Bifurcation module unavailable.",
                import_error=self._import_errors.get("analysis_bifurcation"),
            )

        for class_name in ["Bifurcation", "BifurcationAnalyzer"]:
            cls = getattr(mod, class_name, None)
            if isinstance(cls, type):
                return self._safe_call(cls, *args, **kwargs)

        return self._result_error(
            "No known bifurcation class found.",
            guidance="Inspect tellurium.analysis.bifurcation for available class names.",
        )

    # -------------------------------------------------------------------------
    # plotting API
    # -------------------------------------------------------------------------
    def call_new_plot(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a new plot through tellurium.plotting.api.

        Returns:
            dict: unified status/result.
        """
        return self._call_attr("plotting_api", "newPlot", *args, **kwargs)

    def call_plot(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic plotting entrypoint.

        Returns:
            dict: unified status/result.
        """
        # prefer package-level plot, then plotting.api.plot
        res = self._call_attr("tellurium_pkg", "plot", *args, **kwargs)
        if res["status"] == "fallback" or res["status"] == "error":
            return self._call_attr("plotting_api", "plot", *args, **kwargs)
        return res

    # -------------------------------------------------------------------------
    # utility helpers
    # -------------------------------------------------------------------------
    def call_omex_list_contents(self, omex_path: str) -> Dict[str, Any]:
        """
        List OMEX archive content using tellurium.utils.omex where available.

        Args:
            omex_path: Path to OMEX archive.

        Returns:
            dict: unified status/result.
        """
        mod = self._get_module("utils_omex")
        if mod is None:
            return self._result_fallback(
                "OMEX utility module unavailable.",
                import_error=self._import_errors.get("utils_omex"),
            )

        for name in ["listContents", "getLocationsByFormat", "readManifestEntries"]:
            fn = getattr(mod, name, None)
            if callable(fn):
                return self._safe_call(fn, omex_path)

        return self._result_error(
            "No known OMEX content function found.",
            guidance="Inspect tellurium.utils.omex and select available API methods.",
        )

    def call_misc(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Invoke a function in tellurium.utils.misc by name.

        Args:
            function_name: Exact function attribute name.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: unified status/result.
        """
        mod = self._get_module("utils_misc")
        if mod is None:
            return self._result_fallback(
                "Misc utility module unavailable.",
                import_error=self._import_errors.get("utils_misc"),
            )
        fn = getattr(mod, function_name, None)
        if not callable(fn):
            return self._result_error(
                f"Function '{function_name}' not found in tellurium.utils.misc.",
                guidance="Use dir(tellurium.utils.misc) to discover valid function names.",
            )
        return self._safe_call(fn, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Generic execution bridge
    # -------------------------------------------------------------------------
    def call(self, module_key: str, attribute: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Generic bridge to call any imported module attribute.

        Args:
            module_key: One of known internal keys from adapter target registry.
            attribute: Function/class name in target module.
            *args: Positional arguments.
            **kwargs: Keyword arguments.

        Returns:
            dict: unified status/result.
        """
        if module_key not in self._targets:
            return self._result_error(
                f"Unknown module key '{module_key}'.",
                available_module_keys=list(self._targets.keys()),
            )
        mod = self._get_module(module_key)
        if mod is None:
            return self._result_fallback(
                f"Module '{self._targets[module_key]}' unavailable.",
                import_error=self._import_errors.get(module_key),
            )
        obj = getattr(mod, attribute, None)
        if obj is None:
            return self._result_error(
                f"Attribute '{attribute}' not found in '{self._targets[module_key]}'."
            )
        if callable(obj):
            return self._safe_call(obj, *args, **kwargs)
        return self._result_success(result=obj)