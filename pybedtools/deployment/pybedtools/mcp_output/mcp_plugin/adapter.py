import os
import sys
import importlib
import traceback
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for pybedtools repository integration.

    This adapter prioritizes direct Python imports and provides graceful CLI-oriented guidance
    when import/runtime requirements are unavailable (for example, missing external `bedtools` binary).
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._errors: List[str] = []
        self._load_modules()

    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _load_module(self, key: str, module_path: str) -> None:
        try:
            self._modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self._modules[key] = None
            self._errors.append(
                f"Failed to import '{module_path}': {exc}. "
                f"Action: ensure repository source is present under 'source/' and dependencies are installed."
            )

    def _load_modules(self) -> None:
        self._load_module("pybedtools", "pybedtools")
        self._load_module("scripts_annotate", "pybedtools.scripts.annotate")
        self._load_module("scripts_intersection_matrix", "pybedtools.scripts.intersection_matrix")
        self._load_module("scripts_intron_exon_reads", "pybedtools.scripts.intron_exon_reads")
        self._load_module("scripts_peak_pie", "pybedtools.scripts.peak_pie")
        self._load_module("scripts_venn_gchart", "pybedtools.scripts.venn_gchart")
        self._load_module("scripts_venn_mpl", "pybedtools.scripts.venn_mpl")
        self._load_module("contrib_bigbed", "pybedtools.contrib.bigbed")
        self._load_module("contrib_bigwig", "pybedtools.contrib.bigwig")
        self._load_module("contrib_intersection_matrix", "pybedtools.contrib.intersection_matrix")
        self._load_module("contrib_long_range_interaction", "pybedtools.contrib.long_range_interaction")
        self._load_module("contrib_plotting", "pybedtools.contrib.plotting")
        self._load_module("contrib_venn_maker", "pybedtools.contrib.venn_maker")
        self._load_module("helpers", "pybedtools.helpers")
        self._load_module("parallel", "pybedtools.parallel")
        self._load_module("stats", "pybedtools.stats")
        self._load_module("paths", "pybedtools.paths")
        self._load_module("settings", "pybedtools.settings")
        self._load_module("genome_registry", "pybedtools.genome_registry")

    def health_check(self) -> Dict[str, Any]:
        """
        Validate import readiness and provide environment diagnostics.

        Returns:
            dict: Unified status payload with import errors and actionable hints.
        """
        missing = [k for k, v in self._modules.items() if v is None]
        hints = []
        if missing:
            hints.append("Some modules failed to import. Verify source path and Python dependencies.")
        hints.append("pybedtools requires external BEDTools binary available on PATH.")
        return self._result(
            "success" if not missing else "partial",
            mode=self.mode,
            imported_modules=[k for k, v in self._modules.items() if v is not None],
            missing_modules=missing,
            errors=self._errors,
            guidance=hints,
        )

    # -------------------------------------------------------------------------
    # Core object creation
    # -------------------------------------------------------------------------

    def create_bedtool(self, data: Optional[Any] = None, from_string: bool = False, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a pybedtools.BedTool instance.

        Parameters:
            data: Input data (path, interval string, iterable, etc.).
            from_string: If True, treats `data` as BED content string.
            **kwargs: Additional keyword arguments forwarded to BedTool constructor.

        Returns:
            dict: status + instance or error details.
        """
        mod = self._modules.get("pybedtools")
        if mod is None:
            return self._result(
                "error",
                message="pybedtools module is unavailable.",
                guidance="Install dependencies and ensure source repository is mounted under source/.",
            )
        try:
            if data is None:
                obj = mod.BedTool("", from_string=True, **kwargs)
            else:
                obj = mod.BedTool(data, from_string=from_string, **kwargs)
            return self._result("success", instance=obj, type="BedTool")
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to create BedTool: {exc}",
                traceback=traceback.format_exc(),
                guidance="Check input format and ensure BEDTools binary is available on PATH.",
            )

    def create_interval(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create a pybedtools.Interval instance.

        Parameters:
            *args: Positional arguments for Interval.
            **kwargs: Keyword arguments for Interval.

        Returns:
            dict: status + instance or error details.
        """
        mod = self._modules.get("pybedtools")
        if mod is None or not hasattr(mod, "Interval"):
            return self._result(
                "error",
                message="Interval class is unavailable.",
                guidance="Verify pybedtools import and version compatibility.",
            )
        try:
            obj = mod.Interval(*args, **kwargs)
            return self._result("success", instance=obj, type="Interval")
        except Exception as exc:
            return self._result("error", message=f"Failed to create Interval: {exc}", traceback=traceback.format_exc())

    # -------------------------------------------------------------------------
    # Generic function/class dispatch helpers
    # -------------------------------------------------------------------------

    def call_module_function(self, module_key: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function by module key and function name.

        Parameters:
            module_key: Internal module registry key.
            function_name: Callable name in the module.
            *args/**kwargs: Forwarded call parameters.

        Returns:
            dict: Unified status payload with result or error.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result(
                "error",
                message=f"Module '{module_key}' is not available.",
                guidance="Run health_check() and resolve missing imports.",
            )
        fn = getattr(mod, function_name, None)
        if fn is None or not callable(fn):
            return self._result(
                "error",
                message=f"Function '{function_name}' not found in module '{module_key}'.",
                guidance="Inspect module API and pass a valid function name.",
            )
        try:
            return self._result("success", result=fn(*args, **kwargs))
        except Exception as exc:
            return self._result(
                "error",
                message=f"Function call failed for {module_key}.{function_name}: {exc}",
                traceback=traceback.format_exc(),
                guidance="Check parameters and external tool availability.",
            )

    def create_module_class_instance(
        self, module_key: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Instantiate a class by module key and class name.

        Parameters:
            module_key: Internal module registry key.
            class_name: Class name in the module.
            *args/**kwargs: Constructor parameters.

        Returns:
            dict: Unified status payload with instance or error.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result("error", message=f"Module '{module_key}' is unavailable.")
        cls = getattr(mod, class_name, None)
        if cls is None or not isinstance(cls, type):
            return self._result(
                "error",
                message=f"Class '{class_name}' not found in module '{module_key}'.",
                guidance="Use introspect_module() to discover available classes.",
            )
        try:
            return self._result("success", instance=cls(*args, **kwargs), type=class_name)
        except Exception as exc:
            return self._result(
                "error",
                message=f"Failed to instantiate {module_key}.{class_name}: {exc}",
                traceback=traceback.format_exc(),
            )

    def introspect_module(self, module_key: str) -> Dict[str, Any]:
        """
        List callable functions and classes in a loaded module.

        Parameters:
            module_key: Internal module registry key.

        Returns:
            dict: status + discovered API entries.
        """
        mod = self._modules.get(module_key)
        if mod is None:
            return self._result("error", message=f"Module '{module_key}' is unavailable.")
        try:
            names = dir(mod)
            functions = []
            classes = []
            for n in names:
                if n.startswith("_"):
                    continue
                obj = getattr(mod, n, None)
                if callable(obj):
                    if isinstance(obj, type):
                        classes.append(n)
                    else:
                        functions.append(n)
            return self._result("success", module=module_key, functions=functions, classes=classes)
        except Exception as exc:
            return self._result("error", message=f"Introspection failed: {exc}", traceback=traceback.format_exc())

    # -------------------------------------------------------------------------
    # CLI-script module wrappers (identified in analysis)
    # -------------------------------------------------------------------------

    def run_annotate(self, function_name: str = "main", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("scripts_annotate", function_name, *args, **kwargs)

    def run_intersection_matrix(self, function_name: str = "main", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("scripts_intersection_matrix", function_name, *args, **kwargs)

    def run_intron_exon_reads(self, function_name: str = "main", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("scripts_intron_exon_reads", function_name, *args, **kwargs)

    def run_peak_pie(self, function_name: str = "main", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("scripts_peak_pie", function_name, *args, **kwargs)

    def run_venn_gchart(self, function_name: str = "main", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("scripts_venn_gchart", function_name, *args, **kwargs)

    def run_venn_mpl(self, function_name: str = "main", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("scripts_venn_mpl", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Contrib module wrappers
    # -------------------------------------------------------------------------

    def call_bigbed(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("contrib_bigbed", function_name, *args, **kwargs)

    def call_bigwig(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("contrib_bigwig", function_name, *args, **kwargs)

    def call_contrib_intersection_matrix(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("contrib_intersection_matrix", function_name, *args, **kwargs)

    def call_long_range_interaction(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("contrib_long_range_interaction", function_name, *args, **kwargs)

    def call_plotting(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("contrib_plotting", function_name, *args, **kwargs)

    def call_venn_maker(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("contrib_venn_maker", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Utility module wrappers
    # -------------------------------------------------------------------------

    def call_helpers(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("helpers", function_name, *args, **kwargs)

    def call_parallel(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("parallel", function_name, *args, **kwargs)

    def call_stats(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("stats", function_name, *args, **kwargs)

    def call_paths(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("paths", function_name, *args, **kwargs)

    def call_settings(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("settings", function_name, *args, **kwargs)

    def call_genome_registry(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("genome_registry", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Fallback guidance
    # -------------------------------------------------------------------------

    def fallback_guidance(self) -> Dict[str, Any]:
        """
        Provide fallback guidance when import mode is partially unavailable.

        Returns:
            dict: status + concise next-step recommendations.
        """
        return self._result(
            "success",
            mode=self.mode,
            message="Import mode fallback guidance",
            guidance=[
                "Install required Python dependencies: numpy, pysam.",
                "Install optional packages as needed: matplotlib, pyBigWig, bx-python, genomepy.",
                "Install BEDTools and ensure `bedtools` executable is available on PATH.",
                "If script execution is needed, use run_* methods and pass supported callable names.",
                "Use health_check() and introspect_module(<module_key>) to troubleshoot APIs.",
            ],
        )