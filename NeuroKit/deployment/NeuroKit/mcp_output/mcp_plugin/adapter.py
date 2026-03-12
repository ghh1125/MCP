import os
import sys
import importlib
import inspect
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for NeuroKit repository.

    This adapter dynamically imports the local repository package from the configured
    source path and exposes a unified, error-safe API for:
    - module inventory
    - callable discovery
    - dynamic function execution
    - dynamic class instantiation
    - targeted high-value wrappers for common NeuroKit workflows

    All public methods return a dictionary with a mandatory 'status' field.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter in import mode and attempt loading NeuroKit package.

        Attributes:
            mode (str): Execution mode. Always initialized to 'import'.
            package_root (str): Root package name for the imported repository.
            fallback_mode (bool): True when import failed and fallback behavior is active.
        """
        self.mode = "import"
        self.package_root = "neurokit2"
        self.fallback_mode = False
        self._root_module = None
        self._module_cache: Dict[str, Any] = {}
        self._load_error: Optional[str] = None

        self._known_modules: List[str] = [
            "neurokit2",
            "neurokit2.benchmark",
            "neurokit2.bio",
            "neurokit2.complexity",
            "neurokit2.data",
            "neurokit2.ecg",
            "neurokit2.eda",
            "neurokit2.eeg",
            "neurokit2.emg",
            "neurokit2.eog",
            "neurokit2.epochs",
            "neurokit2.events",
            "neurokit2.hrv",
            "neurokit2.markov",
            "neurokit2.microstates",
            "neurokit2.misc",
            "neurokit2.ppg",
            "neurokit2.rsp",
            "neurokit2.signal",
            "neurokit2.stats",
            "neurokit2.video",
        ]

        self._import_root()

    def _import_root(self) -> None:
        """Attempt to import root package and set fallback flags."""
        try:
            self._root_module = importlib.import_module(self.package_root)
            self._module_cache[self.package_root] = self._root_module
        except Exception as exc:
            self.fallback_mode = True
            self._load_error = str(exc)

    def _ok(self, **kwargs: Any) -> Dict[str, Any]:
        """Build success response."""
        payload = {"status": "success", "mode": self.mode, "fallback_mode": self.fallback_mode}
        payload.update(kwargs)
        return payload

    def _err(self, message: str, guidance: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
        """Build error response with actionable guidance."""
        payload = {"status": "error", "mode": self.mode, "fallback_mode": self.fallback_mode, "error": message}
        if guidance:
            payload["guidance"] = guidance
        payload.update(kwargs)
        return payload

    def health(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import status.

        Returns:
            Dict[str, Any]: Unified status payload including source path and import details.
        """
        if self.fallback_mode:
            return self._err(
                message="NeuroKit import failed. Adapter is running in fallback mode.",
                guidance=(
                    "Ensure repository source is available under the expected 'source' directory "
                    "and dependencies are installed (numpy, scipy, pandas, matplotlib)."
                ),
                source_path=source_path,
                import_error=self._load_error,
                package=self.package_root,
            )
        return self._ok(source_path=source_path, package=self.package_root, loaded=True)

    # -------------------------------------------------------------------------
    # Discovery APIs
    # -------------------------------------------------------------------------
    def list_modules(self) -> Dict[str, Any]:
        """
        List known NeuroKit modules from repository analysis.

        Returns:
            Dict[str, Any]: Status payload with module names.
        """
        return self._ok(modules=self._known_modules)

    def import_module(self, module_path: str) -> Dict[str, Any]:
        """
        Import a module by full package path and cache it.

        Args:
            module_path (str): Full module path (e.g., 'neurokit2.ecg').

        Returns:
            Dict[str, Any]: Status payload with module metadata.
        """
        if self.fallback_mode:
            return self._err(
                message="Cannot import modules in fallback mode.",
                guidance="Fix root import first using health() diagnostics.",
                module_path=module_path,
            )
        try:
            mod = importlib.import_module(module_path)
            self._module_cache[module_path] = mod
            return self._ok(module_path=module_path, imported=True, file=getattr(mod, "__file__", None))
        except Exception as exc:
            return self._err(
                message=f"Failed to import module '{module_path}': {exc}",
                guidance="Verify module path and dependency availability.",
                module_path=module_path,
            )

    def list_callables(self, module_path: str) -> Dict[str, Any]:
        """
        Enumerate public callables (functions/classes) in a module.

        Args:
            module_path (str): Full module path.

        Returns:
            Dict[str, Any]: Status payload with callable names and basic signatures.
        """
        try:
            mod = self._module_cache.get(module_path) or importlib.import_module(module_path)
            self._module_cache[module_path] = mod
            callables = []
            for name, obj in inspect.getmembers(mod):
                if name.startswith("_"):
                    continue
                if inspect.isfunction(obj) or inspect.isclass(obj):
                    try:
                        sig = str(inspect.signature(obj))
                    except Exception:
                        sig = "(signature unavailable)"
                    callables.append({"name": name, "type": "class" if inspect.isclass(obj) else "function", "signature": sig})
            return self._ok(module_path=module_path, callables=callables, count=len(callables))
        except Exception as exc:
            return self._err(
                message=f"Failed to inspect module '{module_path}': {exc}",
                guidance="Import the module first and ensure optional dependencies are installed.",
                module_path=module_path,
            )

    # -------------------------------------------------------------------------
    # Dynamic execution APIs
    # -------------------------------------------------------------------------
    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function dynamically from a specified module.

        Args:
            module_path (str): Full module path.
            function_name (str): Function name in module.
            *args: Positional arguments forwarded to function.
            **kwargs: Keyword arguments forwarded to function.

        Returns:
            Dict[str, Any]: Status payload including function result.
        """
        if self.fallback_mode:
            return self._err(
                message="Function calls are unavailable in fallback mode.",
                guidance="Resolve import issues and retry.",
                module_path=module_path,
                function_name=function_name,
            )
        try:
            mod = self._module_cache.get(module_path) or importlib.import_module(module_path)
            self._module_cache[module_path] = mod
            fn = getattr(mod, function_name, None)
            if fn is None or not callable(fn):
                return self._err(
                    message=f"Function '{function_name}' not found in module '{module_path}'.",
                    guidance="Use list_callables() to inspect available functions.",
                    module_path=module_path,
                    function_name=function_name,
                )
            result = fn(*args, **kwargs)
            return self._ok(module_path=module_path, function_name=function_name, result=result)
        except Exception as exc:
            return self._err(
                message=f"Function call failed for '{module_path}.{function_name}': {exc}",
                guidance="Validate input arguments and install optional dependencies if required.",
                module_path=module_path,
                function_name=function_name,
            )

    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate a class dynamically from a specified module.

        Args:
            module_path (str): Full module path.
            class_name (str): Class name in module.
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            Dict[str, Any]: Status payload including created instance.
        """
        if self.fallback_mode:
            return self._err(
                message="Class instantiation is unavailable in fallback mode.",
                guidance="Resolve import issues and retry.",
                module_path=module_path,
                class_name=class_name,
            )
        try:
            mod = self._module_cache.get(module_path) or importlib.import_module(module_path)
            self._module_cache[module_path] = mod
            cls = getattr(mod, class_name, None)
            if cls is None or not inspect.isclass(cls):
                return self._err(
                    message=f"Class '{class_name}' not found in module '{module_path}'.",
                    guidance="Use list_callables() to inspect available classes.",
                    module_path=module_path,
                    class_name=class_name,
                )
            instance = cls(*args, **kwargs)
            return self._ok(module_path=module_path, class_name=class_name, instance=instance)
        except Exception as exc:
            return self._err(
                message=f"Class instantiation failed for '{module_path}.{class_name}': {exc}",
                guidance="Check constructor parameters and module compatibility.",
                module_path=module_path,
                class_name=class_name,
            )

    # -------------------------------------------------------------------------
    # High-value convenience wrappers (core analysis-driven usage)
    # -------------------------------------------------------------------------
    def nk_call(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a top-level neurokit2 function by name.

        Args:
            function_name (str): Exported function in neurokit2 namespace.
            *args: Positional args.
            **kwargs: Keyword args.

        Returns:
            Dict[str, Any]: Unified status payload with result.
        """
        return self.call_function("neurokit2", function_name, *args, **kwargs)

    def ecg_pipeline(self, signal: Any, sampling_rate: int = 1000, method: str = "neurokit") -> Dict[str, Any]:
        """
        Run common ECG processing pipeline using neurokit2.ecg_process.

        Args:
            signal (Any): Raw ECG signal array-like.
            sampling_rate (int): Signal sampling frequency in Hz.
            method (str): Cleaning/processing strategy supported by NeuroKit.

        Returns:
            Dict[str, Any]: Status payload with processed signals and info.
        """
        return self.call_function(
            "neurokit2.ecg.ecg_process",
            "ecg_process",
            signal,
            sampling_rate=sampling_rate,
            method=method,
        )

    def eda_pipeline(self, signal: Any, sampling_rate: int = 1000, method: str = "neurokit") -> Dict[str, Any]:
        """
        Run common EDA processing pipeline using neurokit2.eda.eda_process.

        Args:
            signal (Any): Raw EDA signal array-like.
            sampling_rate (int): Sampling frequency in Hz.
            method (str): Method option supported by NeuroKit.

        Returns:
            Dict[str, Any]: Status payload with processed signals and info.
        """
        return self.call_function(
            "neurokit2.eda.eda_process",
            "eda_process",
            signal,
            sampling_rate=sampling_rate,
            method=method,
        )

    def rsp_pipeline(self, signal: Any, sampling_rate: int = 1000, method: str = "khodadad2018") -> Dict[str, Any]:
        """
        Run common respiration processing pipeline using neurokit2.rsp.rsp_process.

        Args:
            signal (Any): Raw respiration signal array-like.
            sampling_rate (int): Sampling frequency in Hz.
            method (str): Processing method.

        Returns:
            Dict[str, Any]: Status payload with processed signals and info.
        """
        return self.call_function(
            "neurokit2.rsp.rsp_process",
            "rsp_process",
            signal,
            sampling_rate=sampling_rate,
            method=method,
        )

    def ppg_pipeline(self, signal: Any, sampling_rate: int = 1000, method: str = "elgendi") -> Dict[str, Any]:
        """
        Run common PPG processing pipeline using neurokit2.ppg.ppg_process.

        Args:
            signal (Any): Raw PPG signal array-like.
            sampling_rate (int): Sampling frequency in Hz.
            method (str): Peak/processing method.

        Returns:
            Dict[str, Any]: Status payload with processed signals and info.
        """
        return self.call_function(
            "neurokit2.ppg.ppg_process",
            "ppg_process",
            signal,
            sampling_rate=sampling_rate,
            method=method,
        )

    def bio_pipeline(self, data: Any, sampling_rate: int = 1000) -> Dict[str, Any]:
        """
        Run multimodal biosignal processing using neurokit2.bio.bio_process.

        Args:
            data (Any): DataFrame or dict-like structure of biosignals.
            sampling_rate (int): Sampling frequency in Hz.

        Returns:
            Dict[str, Any]: Status payload with processed dataframe and metadata.
        """
        return self.call_function(
            "neurokit2.bio.bio_process",
            "bio_process",
            data,
            sampling_rate=sampling_rate,
        )