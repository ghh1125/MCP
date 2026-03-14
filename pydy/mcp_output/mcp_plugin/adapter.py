import os
import sys
import importlib
import traceback
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the pydy repository.

    This adapter attempts direct imports from the local source tree first.
    If imports fail, it switches to graceful fallback behavior while keeping a
    consistent response format for all methods.
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        """
        Initialize adapter state and attempt module/function/class imports.

        Attributes:
            mode (str): Adapter operation mode, defaults to "import".
            available (bool): Whether primary imports are available.
            modules (dict): Loaded module objects.
            symbols (dict): Imported callable/class symbols.
            errors (dict): Import-time errors keyed by symbol/module name.
        """
        self.mode = "import"
        self.available = False
        self.modules: Dict[str, Any] = {}
        self.symbols: Dict[str, Any] = {}
        self.errors: Dict[str, str] = {}
        self._load_imports()

    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, guidance: str, details: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
            "guidance": guidance,
        }
        if details:
            payload["details"] = details
        return payload

    def _fallback(self, feature: str) -> Dict[str, Any]:
        return self._err(
            message=f"Feature unavailable in current environment: {feature}",
            guidance=(
                "Verify local source checkout under the 'source' directory, ensure dependencies "
                "are installed (sympy, numpy, scipy), and retry import mode."
            ),
        )

    def _load_module(self, key: str, module_path: str) -> None:
        try:
            self.modules[key] = importlib.import_module(module_path)
        except Exception as exc:
            self.errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_symbol(self, key: str, module_key: str, symbol_name: str) -> None:
        try:
            module = self.modules[module_key]
            self.symbols[key] = getattr(module, symbol_name)
        except Exception as exc:
            self.errors[key] = f"{type(exc).__name__}: {exc}"

    def _load_imports(self) -> None:
        # Full module paths derived from analysis packages (without "source." prefix)
        self._load_module("benchmark", "bin.benchmark_pydy_code_gen")
        self._load_module("compare", "bin.compare_linear_systems_solvers")
        self._load_module("kane6_util", "examples.Kane1985.Chapter6.util")

        # parallel-execution directory uses hyphen; cannot import as package path directly.
        # Graceful handling kept explicit for transparency.
        self.errors["parallel_execution_modules"] = (
            "ImportError: Module path 'examples.parallel-execution.*' is not a valid Python package path."
        )

        # Symbols
        if "benchmark" in self.modules:
            self._load_symbol("run_benchmark", "benchmark", "run_benchmark")

        if "compare" in self.modules:
            self._load_symbol("numpy_umath_linalg_solve", "compare", "numpy_umath_linalg_solve")
            self._load_symbol("scipy_linalg_lapack_dposv", "compare", "scipy_linalg_lapack_dposv")
            self._load_symbol("scipy_linalg_solve", "compare", "scipy_linalg_solve")

        if "kane6_util" in self.modules:
            self._load_symbol("function_from_partials", "kane6_util", "function_from_partials")
            self._load_symbol("generalized_active_forces", "kane6_util", "generalized_active_forces")
            self._load_symbol("generalized_active_forces_K", "kane6_util", "generalized_active_forces_K")
            self._load_symbol("PartialVelocity", "kane6_util", "PartialVelocity")

        self.available = len(self.symbols) > 0

    # -------------------------------------------------------------------------
    # Health and diagnostics
    # -------------------------------------------------------------------------
    def health(self) -> Dict[str, Any]:
        """
        Return adapter health diagnostics.

        Returns:
            dict: Unified status payload with loaded module and symbol details.
        """
        return self._ok(
            data={
                "available": self.available,
                "loaded_modules": sorted(self.modules.keys()),
                "loaded_symbols": sorted(self.symbols.keys()),
                "import_errors": self.errors,
            },
            message="adapter initialized",
        )

    # -------------------------------------------------------------------------
    # bin.benchmark_pydy_code_gen
    # -------------------------------------------------------------------------
    def call_run_benchmark(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call benchmark_pydy_code_gen.run_benchmark.

        Parameters:
            *args: Positional arguments forwarded to run_benchmark.
            **kwargs: Keyword arguments forwarded to run_benchmark.

        Returns:
            dict: Unified status payload with invocation result.
        """
        fn = self.symbols.get("run_benchmark")
        if fn is None:
            return self._fallback("bin.benchmark_pydy_code_gen.run_benchmark")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "run_benchmark executed")
        except Exception as exc:
            return self._err(
                "Failed to execute run_benchmark.",
                "Check function arguments and runtime dependencies, then retry.",
                details=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # bin.compare_linear_systems_solvers
    # -------------------------------------------------------------------------
    def call_numpy_umath_linalg_solve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call compare_linear_systems_solvers.numpy_umath_linalg_solve.

        Parameters:
            *args: Positional arguments forwarded to the function.
            **kwargs: Keyword arguments forwarded to the function.

        Returns:
            dict: Unified status payload with solve result.
        """
        fn = self.symbols.get("numpy_umath_linalg_solve")
        if fn is None:
            return self._fallback("bin.compare_linear_systems_solvers.numpy_umath_linalg_solve")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "numpy_umath_linalg_solve executed")
        except Exception as exc:
            return self._err(
                "Failed to execute numpy_umath_linalg_solve.",
                "Ensure matrix dimensions and numeric dtypes are valid.",
                details=f"{type(exc).__name__}: {exc}",
            )

    def call_scipy_linalg_lapack_dposv(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call compare_linear_systems_solvers.scipy_linalg_lapack_dposv.

        Parameters:
            *args: Positional arguments forwarded to the function.
            **kwargs: Keyword arguments forwarded to the function.

        Returns:
            dict: Unified status payload with solve result.
        """
        fn = self.symbols.get("scipy_linalg_lapack_dposv")
        if fn is None:
            return self._fallback("bin.compare_linear_systems_solvers.scipy_linalg_lapack_dposv")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "scipy_linalg_lapack_dposv executed")
        except Exception as exc:
            return self._err(
                "Failed to execute scipy_linalg_lapack_dposv.",
                "Provide a symmetric positive-definite matrix and compatible RHS.",
                details=f"{type(exc).__name__}: {exc}",
            )

    def call_scipy_linalg_solve(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call compare_linear_systems_solvers.scipy_linalg_solve.

        Parameters:
            *args: Positional arguments forwarded to the function.
            **kwargs: Keyword arguments forwarded to the function.

        Returns:
            dict: Unified status payload with solve result.
        """
        fn = self.symbols.get("scipy_linalg_solve")
        if fn is None:
            return self._fallback("bin.compare_linear_systems_solvers.scipy_linalg_solve")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "scipy_linalg_solve executed")
        except Exception as exc:
            return self._err(
                "Failed to execute scipy_linalg_solve.",
                "Validate input array shapes and that SciPy is installed correctly.",
                details=f"{type(exc).__name__}: {exc}",
            )

    # -------------------------------------------------------------------------
    # examples.Kane1985.Chapter6.util
    # -------------------------------------------------------------------------
    def create_partial_velocity_instance(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of examples.Kane1985.Chapter6.util.PartialVelocity.

        Parameters:
            *args: Positional constructor arguments.
            **kwargs: Keyword constructor arguments.

        Returns:
            dict: Unified status payload with created instance.
        """
        cls = self.symbols.get("PartialVelocity")
        if cls is None:
            return self._fallback("examples.Kane1985.Chapter6.util.PartialVelocity")
        try:
            instance = cls(*args, **kwargs)
            return self._ok({"instance": instance}, "PartialVelocity instance created")
        except Exception as exc:
            return self._err(
                "Failed to instantiate PartialVelocity.",
                "Verify constructor arguments required by the class.",
                details=f"{type(exc).__name__}: {exc}",
            )

    def call_function_from_partials(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call examples.Kane1985.Chapter6.util.function_from_partials.

        Parameters:
            *args: Positional arguments forwarded to the function.
            **kwargs: Keyword arguments forwarded to the function.

        Returns:
            dict: Unified status payload with function result.
        """
        fn = self.symbols.get("function_from_partials")
        if fn is None:
            return self._fallback("examples.Kane1985.Chapter6.util.function_from_partials")
        try:
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, "function_from_partials executed")
        except Exception as exc:
            return self._err(
                "Failed to execute function_from_partials.",
                "Check symbolic inputs and partial definitions for compatibility.",
                details=f"{type(exc).__name__}: {exc}",
            )

    def call_generalized_active_forces(self, *args: Any, **kwargs: Any) -> Dict[str, Any