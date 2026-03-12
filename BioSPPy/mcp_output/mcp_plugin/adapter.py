import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import-mode adapter for BioSPPy repository.

    This adapter attempts to import BioSPPy modules directly from the local `source`
    path and provides unified, safe wrappers for common functionality.
    All method responses use a standardized dictionary format:
        {
            "status": "success" | "error",
            "mode": "import" | "fallback",
            "message": str,
            "data": Any
        }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_modules()

    def _result(self, status: str, message: str, data: Any = None) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "message": message,
            "data": data,
        }

    def _load_modules(self) -> None:
        module_names = [
            "biosppy",
            "biosppy.biometrics",
            "biosppy.clustering",
            "biosppy.metrics",
            "biosppy.plotting",
            "biosppy.quality",
            "biosppy.stats",
            "biosppy.storage",
            "biosppy.timing",
            "biosppy.utils",
            "biosppy.features.cepstral",
            "biosppy.features.frequency",
            "biosppy.features.phase_space",
            "biosppy.features.time",
            "biosppy.features.time_freq",
            "biosppy.signals.abp",
            "biosppy.signals.acc",
            "biosppy.signals.bvp",
            "biosppy.signals.ecg",
            "biosppy.signals.eda",
            "biosppy.signals.eeg",
            "biosppy.signals.egm",
            "biosppy.signals.emg",
            "biosppy.signals.hrv",
            "biosppy.signals.pcg",
            "biosppy.signals.ppg",
            "biosppy.signals.resp",
            "biosppy.signals.tools",
            "biosppy.spatial.eam",
            "biosppy.synthesizers.ecg",
            "biosppy.synthesizers.emg",
            "biosppy.inter_plotting.acc",
            "biosppy.inter_plotting.ecg",
        ]

        for name in module_names:
            try:
                self._modules[name] = importlib.import_module(name)
            except Exception as e:
                self._import_errors[name] = str(e)

        if "biosppy" not in self._modules:
            self.mode = "fallback"

    def get_status(self) -> Dict[str, Any]:
        """
        Get adapter/module import status.

        Returns:
            dict: Import mode, loaded modules, and import errors.
        """
        return self._result(
            "success",
            "Adapter status fetched.",
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
            },
        )

    # -------------------------------------------------------------------------
    # Generic invocation utilities
    # -------------------------------------------------------------------------
    def _call_function(
        self, module_name: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        if self.mode != "import":
            return self._result(
                "error",
                "Import mode is unavailable. Ensure repository source is present under the expected source path.",
                None,
            )

        module = self._modules.get(module_name)
        if module is None:
            return self._result(
                "error",
                f"Module '{module_name}' is not available. Check dependencies and import errors.",
                {"import_error": self._import_errors.get(module_name)},
            )

        fn = getattr(module, function_name, None)
        if fn is None:
            return self._result(
                "error",
                f"Function '{function_name}' not found in module '{module_name}'. Verify API compatibility with this repository version.",
                None,
            )

        try:
            output = fn(*args, **kwargs)
            return self._result(
                "success",
                f"Function '{module_name}.{function_name}' executed successfully.",
                output,
            )
        except Exception as e:
            return self._result(
                "error",
                f"Execution failed for '{module_name}.{function_name}': {e}",
                {"traceback": traceback.format_exc()},
            )

    def _create_instance(
        self, module_name: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        if self.mode != "import":
            return self._result(
                "error",
                "Import mode is unavailable. Ensure repository source is present under the expected source path.",
                None,
            )

        module = self._modules.get(module_name)
        if module is None:
            return self._result(
                "error",
                f"Module '{module_name}' is not available. Check dependencies and import errors.",
                {"import_error": self._import_errors.get(module_name)},
            )

        cls = getattr(module, class_name, None)
        if cls is None:
            return self._result(
                "error",
                f"Class '{class_name}' not found in module '{module_name}'. Verify API compatibility with this repository version.",
                None,
            )

        try:
            obj = cls(*args, **kwargs)
            return self._result(
                "success",
                f"Class '{module_name}.{class_name}' instantiated successfully.",
                obj,
            )
        except Exception as e:
            return self._result(
                "error",
                f"Instantiation failed for '{module_name}.{class_name}': {e}",
                {"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # BioSPPy core wrappers
    # -------------------------------------------------------------------------
    def call_biosppy(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a function from biosppy root module.

        Parameters:
            function_name (str): Name of target function in `biosppy`.
            *args: Positional args passed to the function.
            **kwargs: Keyword args passed to the function.

        Returns:
            dict: Unified execution result.
        """
        return self._call_function("biosppy", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Signals wrappers
    # -------------------------------------------------------------------------
    def call_ecg(self, function_name: str = "ecg", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.ecg", function_name, *args, **kwargs)

    def call_eda(self, function_name: str = "eda", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.eda", function_name, *args, **kwargs)

    def call_emg(self, function_name: str = "emg", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.emg", function_name, *args, **kwargs)

    def call_eeg(self, function_name: str = "eeg", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.eeg", function_name, *args, **kwargs)

    def call_resp(self, function_name: str = "resp", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.resp", function_name, *args, **kwargs)

    def call_abp(self, function_name: str = "abp", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.abp", function_name, *args, **kwargs)

    def call_acc(self, function_name: str = "acc", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.acc", function_name, *args, **kwargs)

    def call_bvp(self, function_name: str = "bvp", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.bvp", function_name, *args, **kwargs)

    def call_egm(self, function_name: str = "egm", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.egm", function_name, *args, **kwargs)

    def call_hrv(self, function_name: str = "hrv", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.hrv", function_name, *args, **kwargs)

    def call_pcg(self, function_name: str = "pcg", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.pcg", function_name, *args, **kwargs)

    def call_ppg(self, function_name: str = "ppg", *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.ppg", function_name, *args, **kwargs)

    def call_tools(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.signals.tools", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Feature extraction wrappers
    # -------------------------------------------------------------------------
    def call_feature_time(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.features.time", function_name, *args, **kwargs)

    def call_feature_frequency(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.features.frequency", function_name, *args, **kwargs)

    def call_feature_cepstral(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.features.cepstral", function_name, *args, **kwargs)

    def call_feature_phase_space(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.features.phase_space", function_name, *args, **kwargs)

    def call_feature_time_freq(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.features.time_freq", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Utilities and analytics wrappers
    # -------------------------------------------------------------------------
    def call_biometrics(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.biometrics", function_name, *args, **kwargs)

    def call_clustering(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.clustering", function_name, *args, **kwargs)

    def call_metrics(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.metrics", function_name, *args, **kwargs)

    def call_plotting(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.plotting", function_name, *args, **kwargs)

    def call_quality(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.quality", function_name, *args, **kwargs)

    def call_stats(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.stats", function_name, *args, **kwargs)

    def call_storage(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.storage", function_name, *args, **kwargs)

    def call_timing(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.timing", function_name, *args, **kwargs)

    def call_utils(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.utils", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Spatial / synthesizers / interactive plotting wrappers
    # -------------------------------------------------------------------------
    def call_spatial_eam(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.spatial.eam", function_name, *args, **kwargs)

    def call_synth_ecg(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.synthesizers.ecg", function_name, *args, **kwargs)

    def call_synth_emg(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.synthesizers.emg", function_name, *args, **kwargs)

    def call_inter_plot_acc(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.inter_plotting.acc", function_name, *args, **kwargs)

    def call_inter_plot_ecg(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._call_function("biosppy.inter_plotting.ecg", function_name, *args, **kwargs)

    # -------------------------------------------------------------------------
    # Generic class instance creation (for any discovered class in modules)
    # -------------------------------------------------------------------------
    def create_instance(self, module_name: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of a class from a loaded module.

        Parameters:
            module_name (str): Full module path, e.g., 'biosppy.storage'.
            class_name (str): Class name in that module.
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            dict: Unified result with created object in `data` when successful.
        """
        return self._create_instance(module_name, class_name, *args, **kwargs)