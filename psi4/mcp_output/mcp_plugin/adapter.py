import os
import sys
import traceback
import importlib
import inspect
import subprocess
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for the Psi4 repository.

    This adapter prioritizes in-process imports and provides a CLI fallback path
    for environments where compiled/runtime Psi4 components are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._imports_loaded = False
        self._import_errors: Dict[str, str] = {}
        self._load_imports()

    # -------------------------------------------------------------------------
    # Internal utilities
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "OK") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(
        self,
        message: str,
        error: Optional[Exception] = None,
        guidance: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "status": "error",
            "mode": self.mode,
            "message": message,
        }
        if error is not None:
            payload["error"] = f"{type(error).__name__}: {str(error)}"
        if guidance:
            payload["guidance"] = guidance
        if data:
            payload.update(data)
        return payload

    def _import_module(self, module_path: str) -> Tuple[Optional[Any], Optional[str]]:
        try:
            mod = importlib.import_module(module_path)
            return mod, None
        except Exception as e:
            return None, f"{type(e).__name__}: {str(e)}"

    def _load_imports(self) -> None:
        module_paths = [
            "conda.psi4-path-advisor",
            "conda._conda_vers",
            "psi4.share.psi4.scripts.test_threading",
            "psi4.share.psi4.scripts.apply_license",
            "psi4.share.psi4.scripts.vmd_cube",
            "psi4.share.psi4.basis.primitives.diff_gbs",
            "psi4.run_psi4",
            "psi4",
        ]
        for path in module_paths:
            mod, err = self._import_module(path)
            if mod is not None:
                self._modules[path] = mod
            else:
                self._import_errors[path] = err or "Unknown import error"

        self._imports_loaded = len(self._modules) > 0
        if not self._imports_loaded:
            self.mode = "cli"

    def health(self) -> Dict[str, Any]:
        """
        Return adapter health and import diagnostics.

        Returns:
            dict: Unified status payload with loaded modules and import errors.
        """
        return self._ok(
            {
                "imports_loaded": self._imports_loaded,
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": dict(self._import_errors),
            },
            message="Adapter initialized",
        )

    def _require_module(self, module_path: str) -> Dict[str, Any]:
        mod = self._modules.get(module_path)
        if mod is not None:
            return self._ok({"module": mod})
        return self._err(
            f"Module '{module_path}' is not available in import mode.",
            guidance="Install missing dependencies or use CLI fallback via run_psi4_cli.",
            data={"import_errors": self._import_errors},
        )

    def _call(self, module_path: str, func_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        req = self._require_module(module_path)
        if req["status"] != "success":
            return req
        mod = req["module"]
        try:
            func = getattr(mod, func_name)
            result = func(*args, **kwargs)
            return self._ok({"result": result}, message=f"{func_name} executed")
        except Exception as e:
            return self._err(
                f"Failed to execute '{func_name}' from '{module_path}'.",
                error=e,
                guidance="Validate parameters and runtime prerequisites for this function.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # CLI fallback module
    # -------------------------------------------------------------------------
    def run_psi4_cli(self, args: Optional[list] = None, timeout: int = 300) -> Dict[str, Any]:
        """
        Execute Psi4 via CLI fallback.

        Parameters:
            args (list, optional): Additional CLI arguments, e.g. ['-i', 'input.dat'].
            timeout (int): Max execution time in seconds.

        Returns:
            dict: Unified status payload containing return code and output streams.
        """
        args = args or []
        cmd = ["psi4"] + args
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            status = "success" if proc.returncode == 0 else "error"
            return {
                "status": status,
                "mode": "cli",
                "message": "CLI command executed",
                "command": cmd,
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        except FileNotFoundError as e:
            return self._err(
                "Psi4 CLI not found.",
                error=e,
                guidance="Ensure the 'psi4' executable is installed and available in PATH.",
            )
        except Exception as e:
            return self._err(
                "Failed to execute Psi4 CLI.",
                error=e,
                guidance="Check CLI arguments and environment configuration.",
            )

    # -------------------------------------------------------------------------
    # Class instance method: PreserveWhiteSpaceWrapRawTextHelpFormatter
    # -------------------------------------------------------------------------
    def instance_preserve_whitespace_wrap_raw_text_help_formatter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance of PreserveWhiteSpaceWrapRawTextHelpFormatter.

        Parameters:
            *args: Positional arguments forwarded to class constructor.
            **kwargs: Keyword arguments forwarded to class constructor.

        Returns:
            dict: Unified status payload containing class instance metadata.
        """
        module_path = "conda.psi4-path-advisor"
        req = self._require_module(module_path)
        if req["status"] != "success":
            return req
        mod = req["module"]
        try:
            cls = getattr(mod, "PreserveWhiteSpaceWrapRawTextHelpFormatter")
            instance = cls(*args, **kwargs)
            return self._ok(
                {
                    "instance": instance,
                    "class_name": "PreserveWhiteSpaceWrapRawTextHelpFormatter",
                    "module": module_path,
                },
                message="Class instance created",
            )
        except Exception as e:
            return self._err(
                "Failed to instantiate PreserveWhiteSpaceWrapRawTextHelpFormatter.",
                error=e,
                guidance="Verify constructor arguments match the class signature.",
                data={"traceback": traceback.format_exc()},
            )

    # -------------------------------------------------------------------------
    # Function wrappers: conda.psi4-path-advisor
    # -------------------------------------------------------------------------
    def call_compiler_type(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call compiler_type from conda.psi4-path-advisor.

        Parameters:
            *args: Positional arguments accepted by compiler_type.
            **kwargs: Keyword arguments accepted by compiler_type.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("conda.psi4-path-advisor", "compiler_type", *args, **kwargs)

    def call_compute_width(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call compute_width from conda.psi4-path-advisor.

        Parameters:
            *args: Positional arguments accepted by compute_width.
            **kwargs: Keyword arguments accepted by compute_width.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("conda.psi4-path-advisor", "compute_width", *args, **kwargs)

    def call_conda_info(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call conda_info from conda.psi4-path-advisor.

        Parameters:
            *args: Positional arguments accepted by conda_info.
            **kwargs: Keyword arguments accepted by conda_info.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("conda.psi4-path-advisor", "conda_info", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function wrappers: conda._conda_vers
    # -------------------------------------------------------------------------
    def call_version_func(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call version_func from conda._conda_vers.

        Parameters:
            *args: Positional arguments accepted by version_func.
            **kwargs: Keyword arguments accepted by version_func.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("conda._conda_vers", "version_func", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function wrappers: psi4.share.psi4.scripts.test_threading
    # -------------------------------------------------------------------------
    def call_print_math_ldd(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call print_math_ldd from psi4.share.psi4.scripts.test_threading.

        Parameters:
            *args: Positional arguments accepted by print_math_ldd.
            **kwargs: Keyword arguments accepted by print_math_ldd.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.scripts.test_threading", "print_math_ldd", *args, **kwargs)

    def call_run_psithon_inputs(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call run_psithon_inputs from psi4.share.psi4.scripts.test_threading.

        Parameters:
            *args: Positional arguments accepted by run_psithon_inputs.
            **kwargs: Keyword arguments accepted by run_psithon_inputs.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.scripts.test_threading", "run_psithon_inputs", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function wrappers: psi4.share.psi4.scripts.apply_license
    # -------------------------------------------------------------------------
    def call_check_header(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call check_header from psi4.share.psi4.scripts.apply_license.

        Parameters:
            *args: Positional arguments accepted by check_header.
            **kwargs: Keyword arguments accepted by check_header.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.scripts.apply_license", "check_header", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function wrappers: psi4.share.psi4.scripts.vmd_cube
    # -------------------------------------------------------------------------
    def call_call_montage(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call call_montage from psi4.share.psi4.scripts.vmd_cube.

        Parameters:
            *args: Positional arguments accepted by call_montage.
            **kwargs: Keyword arguments accepted by call_montage.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.scripts.vmd_cube", "call_montage", *args, **kwargs)

    def call_find_cubes(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call find_cubes from psi4.share.psi4.scripts.vmd_cube.

        Parameters:
            *args: Positional arguments accepted by find_cubes.
            **kwargs: Keyword arguments accepted by find_cubes.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.scripts.vmd_cube", "find_cubes", *args, **kwargs)

    def call_find_vmd(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call find_vmd from psi4.share.psi4.scripts.vmd_cube.

        Parameters:
            *args: Positional arguments accepted by find_vmd.
            **kwargs: Keyword arguments accepted by find_vmd.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.scripts.vmd_cube", "find_vmd", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Function wrappers: psi4.share.psi4.basis.primitives.diff_gbs
    # -------------------------------------------------------------------------
    def call_bas_sanitize(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call bas_sanitize from psi4.share.psi4.basis.primitives.diff_gbs.

        Parameters:
            *args: Positional arguments accepted by bas_sanitize.
            **kwargs: Keyword arguments accepted by bas_sanitize.

        Returns:
            dict: Unified status payload with function result.
        """
        return self._call("psi4.share.psi4.basis.primitives.diff_gbs", "bas_sanitize", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Optional helper: introspection
    # -------------------------------------------------------------------------
    def function_signature(self, module_path: str, func_name: str) -> Dict[str, Any]:
        """
        Return callable signature for an imported function.

        Parameters:
            module_path (str): Full module path.
            func_name (str): Function name.

        Returns:
            dict: Unified status payload with signature string.
        """
        req = self._require_module(module_path)
        if req["status"] != "success":
            return req
        try:
            func = getattr(req["module"], func_name)
            sig = str(inspect.signature(func))
            return self._ok({"signature": sig}, message="Signature retrieved")
        except Exception as e:
            return self._err(
                "Failed to retrieve function signature.",
                error=e,
                guidance="Ensure module and function names are correct and importable.",
            )