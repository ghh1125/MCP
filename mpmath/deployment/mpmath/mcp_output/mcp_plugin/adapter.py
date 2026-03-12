import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional, List

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for mpmath repository.

    This adapter prioritizes direct Python import usage from local source code and provides
    graceful fallback guidance if imports fail.

    Unified return format:
        {
            "status": "success" | "error" | "fallback",
            "mode": "import" | "fallback",
            "data": Any,
            "error": str | None,
            "guidance": str | None
        }
    """

    # -------------------------------------------------------------------------
    # Initialization and module management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._load_modules()

    def _result(
        self,
        status: str,
        data: Any = None,
        error: Optional[str] = None,
        guidance: Optional[str] = None,
    ) -> Dict[str, Any]:
        return {
            "status": status,
            "mode": self.mode,
            "data": data,
            "error": error,
            "guidance": guidance,
        }

    def _load_modules(self) -> None:
        module_map = {
            "mpmath": "mpmath",
            "interactive": "mpmath._interactive",
            "main": "mpmath.__main__",
            "ctx_base": "mpmath.ctx_base",
            "ctx_fp": "mpmath.ctx_fp",
            "ctx_iv": "mpmath.ctx_iv",
            "ctx_mp": "mpmath.ctx_mp",
            "ctx_mp_python": "mpmath.ctx_mp_python",
            "function_docs": "mpmath.function_docs",
            "identification": "mpmath.identification",
            "libfp": "mpmath.libfp",
            "usertools": "mpmath.usertools",
            "visualization": "mpmath.visualization",
            "calculus_approximation": "mpmath.calculus.approximation",
            "calculus_differentiation": "mpmath.calculus.differentiation",
            "calculus_extrapolation": "mpmath.calculus.extrapolation",
            "calculus_inverselaplace": "mpmath.calculus.inverselaplace",
            "calculus_odes": "mpmath.calculus.odes",
            "calculus_optimization": "mpmath.calculus.optimization",
            "calculus_polynomials": "mpmath.calculus.polynomials",
            "calculus_quadrature": "mpmath.calculus.quadrature",
            "functions_bessel": "mpmath.functions.bessel",
            "functions_elliptic": "mpmath.functions.elliptic",
            "functions_expintegrals": "mpmath.functions.expintegrals",
            "functions_factorials": "mpmath.functions.factorials",
            "functions_functions": "mpmath.functions.functions",
            "functions_hypergeometric": "mpmath.functions.hypergeometric",
            "functions_orthogonal": "mpmath.functions.orthogonal",
            "functions_qfunctions": "mpmath.functions.qfunctions",
            "functions_rszeta": "mpmath.functions.rszeta",
            "functions_signals": "mpmath.functions.signals",
            "functions_theta": "mpmath.functions.theta",
            "functions_zeta": "mpmath.functions.zeta",
            "functions_zetazeros": "mpmath.functions.zetazeros",
            "libmp_backend": "mpmath.libmp.backend",
            "libmp_gammazeta": "mpmath.libmp.gammazeta",
            "libmp_libelefun": "mpmath.libmp.libelefun",
            "libmp_libhyper": "mpmath.libmp.libhyper",
            "libmp_libintmath": "mpmath.libmp.libintmath",
            "libmp_libmpc": "mpmath.libmp.libmpc",
            "libmp_libmpf": "mpmath.libmp.libmpf",
            "libmp_libmpi": "mpmath.libmp.libmpi",
            "matrices_calculus": "mpmath.matrices.calculus",
            "matrices_eigen": "mpmath.matrices.eigen",
            "matrices_eigen_symmetric": "mpmath.matrices.eigen_symmetric",
            "matrices_linalg": "mpmath.matrices.linalg",
            "matrices_matrices": "mpmath.matrices.matrices",
        }

        try:
            for key, mod_path in module_map.items():
                self._modules[key] = importlib.import_module(mod_path)
            self.mode = "import"
            self._import_error = None
        except Exception as exc:
            self.mode = "fallback"
            self._import_error = f"Import failed: {exc}"
            self._modules = {}

    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and dependency status.
        """
        if self.mode == "import":
            return self._result(
                "success",
                data={
                    "import_mode": True,
                    "repository": "mpmath",
                    "python_requirement": ">=3.8",
                    "optional_dependencies": ["gmpy2", "matplotlib"],
                    "loaded_modules": sorted(list(self._modules.keys())),
                },
            )
        return self._result(
            "fallback",
            data={"import_mode": False},
            error=self._import_error,
            guidance=(
                "Ensure repository source is available under './source' and retry. "
                "You can also run CLI fallback with 'python -m mpmath'."
            ),
        )

    # -------------------------------------------------------------------------
    # Generic execution helpers
    # -------------------------------------------------------------------------
    def call_mpmath(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call a top-level function or access object from mpmath package.

        Parameters:
            function_name: Name of attribute/function in 'mpmath'.
            *args/**kwargs: Forwarded to callable targets.

        Returns:
            Unified status dictionary with function result.
        """
        if self.mode != "import":
            return self._result(
                "fallback",
                error=self._import_error,
                guidance="Import mode unavailable. Use 'python -m mpmath' for interactive CLI fallback.",
            )
        try:
            mpmath_mod = self._modules["mpmath"]
            target = getattr(mpmath_mod, function_name)
            if callable(target):
                return self._result("success", data=target(*args, **kwargs))
            return self._result("success", data=target)
        except AttributeError:
            return self._result(
                "error",
                error=f"Function or attribute '{function_name}' was not found in mpmath.",
                guidance="Check function name spelling and confirm it exists in the repository version.",
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to execute mpmath.{function_name}: {exc}",
                guidance="Validate input arguments and numeric domains for the selected operation.",
            )

    def call_module_function(
        self, module_key: str, function_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Call a function dynamically from any loaded module.

        Parameters:
            module_key: Internal loaded module key (see health_check loaded_modules).
            function_name: Target function or attribute name.
            *args/**kwargs: Forwarded to callable targets.

        Returns:
            Unified status dictionary with call result.
        """
        if self.mode != "import":
            return self._result(
                "fallback",
                error=self._import_error,
                guidance="Import mode unavailable. Ensure source path is correct and retry.",
            )
        try:
            mod = self._modules[module_key]
            target = getattr(mod, function_name)
            if callable(target):
                return self._result("success", data=target(*args, **kwargs))
            return self._result("success", data=target)
        except KeyError:
            return self._result(
                "error",
                error=f"Module key '{module_key}' is not loaded.",
                guidance="Use health_check to inspect available module keys.",
            )
        except AttributeError:
            return self._result(
                "error",
                error=f"Function or attribute '{function_name}' was not found in module '{module_key}'.",
                guidance="Inspect module API and ensure the requested symbol exists.",
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to execute {module_key}.{function_name}: {exc}",
                guidance="Check the function signature and argument compatibility.",
            )

    # -------------------------------------------------------------------------
    # CLI fallback support
    # -------------------------------------------------------------------------
    def run_cli_entry(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run repository CLI entry equivalent to `python -m mpmath`.

        Parameters:
            argv: Optional argv list (without program name). If omitted, empty list is used.

        Returns:
            Unified status dictionary.
        """
        try:
            main_mod = importlib.import_module("mpmath.__main__")
            if hasattr(main_mod, "main") and callable(main_mod.main):
                result = main_mod.main(*(argv or []))
                return self._result("success", data=result)
            return self._result(
                "error",
                error="CLI module loaded, but no callable 'main' entry was found.",
                guidance="Use 'python -m mpmath' directly if module-level execution is required.",
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"CLI execution failed: {exc}",
                guidance="Run 'python -m mpmath' in a shell to inspect interactive startup behavior.",
            )

    # -------------------------------------------------------------------------
    # Class instance helpers (generic, for identified modules)
    # -------------------------------------------------------------------------
    def create_instance(
        self, module_key: str, class_name: str, *args: Any, **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Create an instance from a class in a loaded module.

        Parameters:
            module_key: Internal loaded module key.
            class_name: Class name inside the module.
            *args/**kwargs: Constructor arguments.

        Returns:
            Unified status dictionary with created instance.
        """
        if self.mode != "import":
            return self._result(
                "fallback",
                error=self._import_error,
                guidance="Import mode unavailable. Verify local source layout and retry.",
            )
        try:
            mod = self._modules[module_key]
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._result("success", data=instance)
        except KeyError:
            return self._result(
                "error",
                error=f"Module key '{module_key}' is not loaded.",
                guidance="Check available modules via health_check.",
            )
        except AttributeError:
            return self._result(
                "error",
                error=f"Class '{class_name}' does not exist in module '{module_key}'.",
                guidance="Confirm class name and module selection.",
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to instantiate {module_key}.{class_name}: {exc}",
                guidance="Review constructor parameters and required types.",
            )

    # -------------------------------------------------------------------------
    # Convenience wrappers for major module groups
    # -------------------------------------------------------------------------
    def call_calculus(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_mpmath(function_name, *args, **kwargs)

    def call_functions(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_mpmath(function_name, *args, **kwargs)

    def call_matrices(self, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_mpmath(function_name, *args, **kwargs)

    def get_traceback(self) -> Dict[str, Any]:
        """
        Return current traceback string if called inside exception context.
        """
        try:
            return self._result("success", data=traceback.format_exc())
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to capture traceback: {exc}",
                guidance="Call this method from within an active exception handling context.",
            )