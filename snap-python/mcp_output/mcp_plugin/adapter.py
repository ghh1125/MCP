import os
import sys
import importlib
import importlib.util
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for snap-python repository integration.

    This adapter attempts to import repository-local modules discovered by analysis and
    exposes callable wrappers with unified response dictionaries.

    All public methods return:
    {
        "status": "success" | "error" | "fallback",
        "mode": "import" | "fallback",
        ...
    }
    """

    # -------------------------------------------------------------------------
    # Lifecycle and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt best-effort module loading.
        """
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        data = {"status": status, "mode": self.mode}
        data.update(kwargs)
        return data

    def _safe_import(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as e:
            self._modules[key] = None
            self._import_errors[key] = (
                f"Failed to import '{module_path}'. "
                f"Ensure repository source is available under '{source_path}' and dependencies are installed. "
                f"Details: {e}"
            )

    def _load_hyphen_module(self, key: str, relative_path: str) -> None:
        abs_path = os.path.join(source_path, relative_path)
        try:
            if not os.path.exists(abs_path):
                raise FileNotFoundError(
                    f"Module file not found at '{abs_path}'. Check repository extraction path."
                )
            spec = importlib.util.spec_from_file_location(key, abs_path)
            if spec is None or spec.loader is None:
                raise ImportError(
                    f"Could not create import spec for '{abs_path}'."
                )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            self._modules[key] = module
        except Exception as e:
            self._modules[key] = None
            self._import_errors[key] = (
                f"Failed to load module from '{abs_path}'. "
                f"Verify file presence and Python compatibility. Details: {e}"
            )

    def _load_modules(self) -> None:
        """
        Load all discovered modules/classes/functions from analysis.
        """
        # Classes in setup modules
        self._safe_import("setup_setup", "setup")
        self._safe_import("swig_setup", "swig.setup")

        # Functions in standard importable module
        self._safe_import("genClassFnExt", "swig.gen.genClassFn.archive.genClassFnExt")

        # Functions in modules with hyphenated filenames (manual load)
        self._load_hyphen_module("disp_custom", os.path.join("swig", "gen", "disp-custom.py"))
        self._load_hyphen_module("tneanet_cpp", os.path.join("dev", "examples", "tneanet-cpp.py"))
        self._load_hyphen_module("snapswig_check", os.path.join("dev", "examples", "snapswig-check.py"))

        if self._import_errors:
            self.mode = "fallback"

    def health_check(self) -> Dict[str, Any]:
        """
        Return adapter/module import status.

        Returns:
            dict: Unified status payload with loaded module keys and import errors.
        """
        loaded = [k for k, v in self._modules.items() if v is not None]
        return self._result(
            "success" if not self._import_errors else "fallback",
            loaded_modules=loaded,
            import_errors=self._import_errors,
            guidance=(
                "If imports failed, ensure the repository is present under the configured source path, "
                "and install optional build/runtime dependencies for SWIG-based modules."
            ),
        )

    # -------------------------------------------------------------------------
    # Class instance creators
    # -------------------------------------------------------------------------
    def create_setup_swigbuild(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create instance of setup.SwigBuild.

        Parameters:
            *args: Positional arguments forwarded to setup.SwigBuild constructor.
            **kwargs: Keyword arguments forwarded to setup.SwigBuild constructor.

        Returns:
            dict: status and created instance or actionable error.
        """
        module = self._modules.get("setup_setup")
        if module is None or not hasattr(module, "SwigBuild"):
            return self._result(
                "fallback",
                error="Class 'SwigBuild' in module 'setup' is unavailable.",
                guidance="Ensure 'setup.py' is importable and supports runtime class instantiation.",
            )
        try:
            instance = module.SwigBuild(*args, **kwargs)
            return self._result("success", class_name="SwigBuild", instance=instance)
        except Exception as e:
            return self._result(
                "error",
                error=f"Failed to instantiate setup.SwigBuild: {e}",
                guidance="Check constructor arguments required by distutils/setuptools command classes.",
            )

    def create_setup_swigextension(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create instance of setup.SwigExtension.
        """
        module = self._modules.get("setup_setup")
        if module is None or not hasattr(module, "SwigExtension"):
            return self._result(
                "fallback",
                error="Class 'SwigExtension' in module 'setup' is unavailable.",
                guidance="Ensure setup module loads successfully.",
            )
        try:
            instance = module.SwigExtension(*args, **kwargs)
            return self._result("success", class_name="SwigExtension", instance=instance)
        except Exception as e:
            return self._result(
                "error",
                error=f"Failed to instantiate setup.SwigExtension: {e}",
                guidance="Provide valid extension constructor parameters (name, sources, and config).",
            )

    def create_swig_setup_pkgbuild(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create instance of swig.setup.PkgBuild.
        """
        module = self._modules.get("swig_setup")
        if module is None or not hasattr(module, "PkgBuild"):
            return self._result(
                "fallback",
                error="Class 'PkgBuild' in module 'swig.setup' is unavailable.",
                guidance="Ensure swig setup module is present and importable.",
            )
        try:
            instance = module.PkgBuild(*args, **kwargs)
            return self._result("success", class_name="PkgBuild", instance=instance)
        except Exception as e:
            return self._result(
                "error",
                error=f"Failed to instantiate swig.setup.PkgBuild: {e}",
                guidance="Verify arguments expected by build command classes.",
            )

    def create_swig_setup_swigextension(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create instance of swig.setup.SwigExtension.
        """
        module = self._modules.get("swig_setup")
        if module is None or not hasattr(module, "SwigExtension"):
            return self._result(
                "fallback",
                error="Class 'SwigExtension' in module 'swig.setup' is unavailable.",
                guidance="Ensure swig setup module import succeeds.",
            )
        try:
            instance = module.SwigExtension(*args, **kwargs)
            return self._result("success", class_name="SwigExtension", instance=instance)
        except Exception as e:
            return self._result(
                "error",
                error=f"Failed to instantiate swig.setup.SwigExtension: {e}",
                guidance="Pass valid extension initialization arguments.",
            )

    # -------------------------------------------------------------------------
    # Function call wrappers
    # -------------------------------------------------------------------------
    def call_convert_esubgraph(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call swig.gen.disp-custom.ConvertESubGraph.

        Parameters:
            *args: Forwarded to ConvertESubGraph.
            **kwargs: Forwarded to ConvertESubGraph.
        """
        module = self._modules.get("disp_custom")
        if module is None or not hasattr(module, "ConvertESubGraph"):
            return self._result(
                "fallback",
                error="Function 'ConvertESubGraph' is unavailable.",
                guidance="Check swig/gen/disp-custom.py availability and compatibility.",
            )
        try:
            result = module.ConvertESubGraph(*args, **kwargs)
            return self._result("success", function="ConvertESubGraph", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"ConvertESubGraph execution failed: {e}",
                guidance="Validate argument types and graph object compatibility.",
            )

    def call_convert_graph(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call swig.gen.disp-custom.ConvertGraph.
        """
        module = self._modules.get("disp_custom")
        if module is None or not hasattr(module, "ConvertGraph"):
            return self._result(
                "fallback",
                error="Function 'ConvertGraph' is unavailable.",
                guidance="Check swig/gen/disp-custom.py load status.",
            )
        try:
            result = module.ConvertGraph(*args, **kwargs)
            return self._result("success", function="ConvertGraph", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"ConvertGraph execution failed: {e}",
                guidance="Ensure provided graph parameters match expected SNAP/SWIG types.",
            )

    def call_convert_subgraph(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call swig.gen.disp-custom.ConvertSubGraph.
        """
        module = self._modules.get("disp_custom")
        if module is None or not hasattr(module, "ConvertSubGraph"):
            return self._result(
                "fallback",
                error="Function 'ConvertSubGraph' is unavailable.",
                guidance="Check swig/gen/disp-custom.py and repository source path.",
            )
        try:
            result = module.ConvertSubGraph(*args, **kwargs)
            return self._result("success", function="ConvertSubGraph", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"ConvertSubGraph execution failed: {e}",
                guidance="Review node/edge subset arguments and graph input types.",
            )

    def call_gen_func_call(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call swig.gen.genClassFn.archive.genClassFnExt.genFuncCall.
        """
        module = self._modules.get("genClassFnExt")
        if module is None or not hasattr(module, "genFuncCall"):
            return self._result(
                "fallback",
                error="Function 'genFuncCall' is unavailable.",
                guidance="Ensure module swig.gen.genClassFn.archive.genClassFnExt imports correctly.",
            )
        try:
            result = module.genFuncCall(*args, **kwargs)
            return self._result("success", function="genFuncCall", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"genFuncCall execution failed: {e}",
                guidance="Verify expected inputs for class/function generation utility.",
            )

    def call_get_func_name(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call swig.gen.genClassFn.archive.genClassFnExt.getFuncName.
        """
        module = self._modules.get("genClassFnExt")
        if module is None or not hasattr(module, "getFuncName"):
            return self._result(
                "fallback",
                error="Function 'getFuncName' is unavailable.",
                guidance="Check import status for swig.gen.genClassFn.archive.genClassFnExt.",
            )
        try:
            result = module.getFuncName(*args, **kwargs)
            return self._result("success", function="getFuncName", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"getFuncName execution failed: {e}",
                guidance="Provide input matching expected parser/line format.",
            )

    def call_remove_first_param(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call swig.gen.genClassFn.archive.genClassFnExt.removeFirstParam.
        """
        module = self._modules.get("genClassFnExt")
        if module is None or not hasattr(module, "removeFirstParam"):
            return self._result(
                "fallback",
                error="Function 'removeFirstParam' is unavailable.",
                guidance="Ensure genClassFnExt module loaded without syntax/runtime issues.",
            )
        try:
            result = module.removeFirstParam(*args, **kwargs)
            return self._result("success", function="removeFirstParam", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"removeFirstParam execution failed: {e}",
                guidance="Check parameter string structure before invoking this utility.",
            )

    def call_tneanet_cpp_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call dev.examples.tneanet-cpp.main.
        """
        module = self._modules.get("tneanet_cpp")
        if module is None or not hasattr(module, "main"):
            return self._result(
                "fallback",
                error="Function 'main' in tneanet-cpp is unavailable.",
                guidance="Check file dev/examples/tneanet-cpp.py exists and is valid.",
            )
        try:
            result = module.main(*args, **kwargs)
            return self._result("success", function="tneanet_cpp.main", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"tneanet_cpp.main execution failed: {e}",
                guidance="Confirm runtime prerequisites for example script are met.",
            )

    def call_snapswig_check_main(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call dev.examples.snapswig-check.main.
        """
        module = self._modules.get("snapswig_check")
        if module is None or not hasattr(module, "main"):
            return self._result(
                "fallback",
                error="Function 'main' in snapswig-check is unavailable.",
                guidance="Check file dev/examples/snapswig-check.py exists and imports succeed.",
            )
        try:
            result = module.main(*args, **kwargs)
            return self._result("success", function="snapswig_check.main", result=result)
        except Exception as e:
            return self._result(
                "error",
                error=f"snapswig_check.main execution failed: {e}",
                guidance="Ensure SWIG SNAP extension is built and importable before running checks.",
            )