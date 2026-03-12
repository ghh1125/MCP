import os
import sys
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP import-mode adapter for the PySDM repository.

    This adapter prioritizes direct imports from the repository source tree.
    If import fails, it switches to a graceful fallback mode and returns
    actionable guidance in English.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._errors: Dict[str, str] = {}
        self._import_core_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "OK") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _fail(self, message: str, hint: Optional[str] = None, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if details:
            payload["details"] = details
        return payload

    def _import_module(self, key: str, import_path: str) -> None:
        try:
            module = __import__(import_path, fromlist=["*"])
            self._modules[key] = module
        except Exception as exc:
            self._errors[key] = f"{type(exc).__name__}: {exc}"

    def _import_core_modules(self) -> None:
        imports = {
            "pysdm_root": "PySDM",
            "builder": "PySDM.builder",
            "particulator": "PySDM.particulator",
            "formulae": "PySDM.formulae",
            "backends_numba": "PySDM.backends.numba",
            "backends_thrust_rtc": "PySDM.backends.thrust_rtc",
            "environments_box": "PySDM.environments.box",
            "environments_parcel": "PySDM.environments.parcel",
            "environments_kinematic_1d": "PySDM.environments.kinematic_1d",
            "environments_kinematic_2d": "PySDM.environments.kinematic_2d",
            "dynamics_condensation": "PySDM.dynamics.condensation",
            "dynamics_collision": "PySDM.dynamics.collisions.collision",
            "dynamics_displacement": "PySDM.dynamics.displacement",
            "dynamics_freezing": "PySDM.dynamics.freezing",
            "dynamics_seeding": "PySDM.dynamics.seeding",
            "exporters_netcdf": "PySDM.exporters.netcdf_exporter",
            "exporters_vtk": "PySDM.exporters.vtk_exporter",
            "products_root": "PySDM.products",
        }
        for key, path in imports.items():
            self._import_module(key, path)

        if self._errors:
            self.mode = "fallback"

    # -------------------------------------------------------------------------
    # Status & diagnostics
    # -------------------------------------------------------------------------
    def get_status(self) -> Dict[str, Any]:
        """
        Return adapter status with import diagnostics.

        Returns:
            dict: Unified status dictionary containing mode and import health.
        """
        return self._ok(
            {
                "imported_modules": sorted(list(self._modules.keys())),
                "failed_modules": self._errors,
            },
            message="Adapter status collected.",
        )

    def validate_environment(self) -> Dict[str, Any]:
        """
        Validate minimum runtime dependencies inferred from analysis.

        Required:
            - numpy
            - numba
            - scipy

        Optional:
            - matplotlib
            - netCDF4
            - vtk

        Returns:
            dict: Unified status dictionary with detected dependency info.
        """
        required = ["numpy", "numba", "scipy"]
        optional = ["matplotlib", "netCDF4", "vtk"]
        found_required = {}
        missing_required = []
        found_optional = {}

        for name in required:
            try:
                __import__(name)
                found_required[name] = True
            except Exception:
                found_required[name] = False
                missing_required.append(name)

        for name in optional:
            try:
                __import__(name)
                found_optional[name] = True
            except Exception:
                found_optional[name] = False

        if missing_required:
            return self._fail(
                "Missing required dependencies.",
                hint=f"Install required packages: {', '.join(missing_required)}",
                details="Use your environment manager or pip to install required dependencies.",
            )

        return self._ok(
            {
                "required": found_required,
                "optional": found_optional,
                "import_mode": self.mode,
            },
            message="Environment validation completed.",
        )

    # -------------------------------------------------------------------------
    # Core object factories
    # -------------------------------------------------------------------------
    def create_formulae(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of PySDM.formulae.Formulae.

        Parameters:
            *args: Positional arguments forwarded to Formulae constructor.
            **kwargs: Keyword arguments forwarded to Formulae constructor.

        Returns:
            dict: Unified status dictionary with created object on success.
        """
        if "formulae" not in self._modules:
            return self._fail(
                "Formulae module is not available.",
                hint="Ensure source/PySDM is present and dependencies are installed.",
                details=self._errors.get("formulae"),
            )
        try:
            cls = getattr(self._modules["formulae"], "Formulae", None)
            if cls is None:
                return self._fail("Formulae class not found in PySDM.formulae.")
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj}, message="Formulae instance created.")
        except Exception as exc:
            return self._fail("Failed to create Formulae instance.", details=f"{type(exc).__name__}: {exc}")

    def create_builder(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of PySDM.builder.Builder.

        Parameters:
            *args: Positional arguments for Builder.
            **kwargs: Keyword arguments for Builder.

        Returns:
            dict: Unified status dictionary.
        """
        if "builder" not in self._modules:
            return self._fail("Builder module is not available.", details=self._errors.get("builder"))
        try:
            cls = getattr(self._modules["builder"], "Builder", None)
            if cls is None:
                return self._fail("Builder class not found in PySDM.builder.")
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj}, message="Builder instance created.")
        except Exception as exc:
            return self._fail("Failed to create Builder instance.", details=f"{type(exc).__name__}: {exc}")

    def create_particulator(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of PySDM.particulator.Particulator.

        Returns:
            dict: Unified status dictionary.
        """
        if "particulator" not in self._modules:
            return self._fail("Particulator module is not available.", details=self._errors.get("particulator"))
        try:
            cls = getattr(self._modules["particulator"], "Particulator", None)
            if cls is None:
                return self._fail("Particulator class not found in PySDM.particulator.")
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj}, message="Particulator instance created.")
        except Exception as exc:
            return self._fail("Failed to create Particulator instance.", details=f"{type(exc).__name__}: {exc}")

    # -------------------------------------------------------------------------
    # Backends
    # -------------------------------------------------------------------------
    def create_numba_backend(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create backend instance from PySDM.backends.numba.

        Returns:
            dict: Unified status dictionary.
        """
        key = "backends_numba"
        if key not in self._modules:
            return self._fail("Numba backend module is not available.", details=self._errors.get(key))
        try:
            module = self._modules[key]
            candidate_names = ["Numba", "Backend", "CPU"]
            cls = next((getattr(module, n) for n in candidate_names if hasattr(module, n)), None)
            if cls is None:
                return self._fail("No recognized backend class found in PySDM.backends.numba.")
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj}, message="Numba backend instance created.")
        except Exception as exc:
            return self._fail("Failed to create numba backend instance.", details=f"{type(exc).__name__}: {exc}")

    def create_thrust_rtc_backend(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create backend instance from PySDM.backends.thrust_rtc.

        Returns:
            dict: Unified status dictionary.
        """
        key = "backends_thrust_rtc"
        if key not in self._modules:
            return self._fail("ThrustRTC backend module is not available.", details=self._errors.get(key))
        try:
            module = self._modules[key]
            candidate_names = ["ThrustRTC", "GPU", "Backend"]
            cls = next((getattr(module, n) for n in candidate_names if hasattr(module, n)), None)
            if cls is None:
                return self._fail("No recognized backend class found in PySDM.backends.thrust_rtc.")
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj}, message="ThrustRTC backend instance created.")
        except Exception as exc:
            return self._fail(
                "Failed to create ThrustRTC backend instance.",
                hint="Ensure CUDA/ThrustRTC runtime is installed and accessible.",
                details=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # Environment factories
    # -------------------------------------------------------------------------
    def create_box_environment(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        key = "environments_box"
        if key not in self._modules:
            return self._fail("Box environment module is not available.", details=self._errors.get(key))
        try:
            cls = getattr(self._modules[key], "Box", None)
            if cls is None:
                return self._fail("Box class not found in PySDM.environments.box.")
            return self._ok({"object": cls(*args, **kwargs)}, message="Box environment instance created.")
        except Exception as exc:
            return self._fail("Failed to create Box environment.", details=f"{type(exc).__name__}: {exc}")

    def create_parcel_environment(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        key = "environments_parcel"
        if key not in self._modules:
            return self._fail("Parcel environment module is not available.", details=self._errors.get(key))
        try:
            cls = getattr(self._modules[key], "Parcel", None)
            if cls is None:
                return self._fail("Parcel class not found in PySDM.environments.parcel.")
            return self._ok({"object": cls(*args, **kwargs)}, message="Parcel environment instance created.")
        except Exception as exc:
            return self._fail("Failed to create Parcel environment.", details=f"{type(exc).__name__}: {exc}")

    # -------------------------------------------------------------------------
    # Generic module/class/function access
    # -------------------------------------------------------------------------
    def instantiate_class(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically import a module and instantiate a class.

        Parameters:
            module_path: Full import path, e.g., 'PySDM.dynamics.condensation'
            class_name: Target class name.
            *args/**kwargs: Constructor arguments.

        Returns:
            dict: Unified status dictionary with object on success.
        """
        try:
            module = __import__(module_path, fromlist=["*"])
            cls = getattr(module, class_name, None)
            if cls is None:
                return self._fail(f"Class '{class_name}' was not found in module '{module_path}'.")
            obj = cls(*args, **kwargs)
            return self._ok({"object": obj}, message=f"Instance of {class_name} created.")
        except Exception as exc:
            return self._fail(
                "Failed to instantiate class.",
                hint="Verify module path, class name, and constructor arguments.",
                details=f"{type(exc).__name__}: {exc}",
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Dynamically import a module and call a function.

        Parameters:
            module_path: Full import path, e.g., 'PySDM.physics.trivia'
            function_name: Function name to call.
            *args/**kwargs: Function arguments.

        Returns:
            dict: Unified status dictionary with function result on success.
        """
        try:
            module = __import__(module_path, fromlist=["*"])
            fn = getattr(module, function_name, None)
            if fn is None or not callable(fn):
                return self._fail(f"Function '{function_name}' was not found in module '{module_path}'.")
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, message=f"Function {function_name} executed.")
        except Exception as exc:
            return self._fail(
                "Failed to execute function.",
                hint="Verify module path, function name, and call arguments.",
                details=f"{type(exc).__name__}: {exc}",
            )