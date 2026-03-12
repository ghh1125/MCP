import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for cclib.

    This adapter prioritizes direct Python imports from repository source code and
    provides CLI fallback guidance when import-mode operations are unavailable.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_errors: Dict[str, str] = {}
        self._load_core_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "success", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _err(self, message: str, hint: Optional[str] = None, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if hint:
            payload["hint"] = hint
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _load_module(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return mod
        except Exception as exc:
            self._import_errors[module_path] = str(exc)
            return None

    def _load_core_modules(self) -> None:
        candidates = [
            "cclib",
            "cclib.io.ccio",
            "cclib.io.cjsonreader",
            "cclib.io.cjsonwriter",
            "cclib.io.xyzreader",
            "cclib.io.xyzwriter",
            "cclib.io.moldenwriter",
            "cclib.io.wfxwriter",
            "cclib.scripts.ccget",
            "cclib.scripts.ccwrite",
            "cclib.scripts.ccframe",
            "cclib.scripts.cda",
        ]
        for name in candidates:
            self._load_module(name)

    def _get_callable(self, module_path: str, attr_name: str) -> Any:
        mod = self._modules.get(module_path) or self._load_module(module_path)
        if mod is None:
            raise ImportError(
                f"Failed to import '{module_path}'. Install required dependencies or verify source path."
            )
        fn = getattr(mod, attr_name, None)
        if fn is None:
            raise AttributeError(
                f"'{attr_name}' not found in '{module_path}'. Verify repository version compatibility."
            )
        return fn

    # -------------------------------------------------------------------------
    # Adapter status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check adapter readiness and imported module status.

        Returns:
            dict: Unified status response including loaded modules and import errors.
        """
        return self._ok(
            {
                "loaded_modules": sorted(self._modules.keys()),
                "import_errors": self._import_errors,
                "source_path": source_path,
            },
            message="health check completed",
        )

    # -------------------------------------------------------------------------
    # cclib high-level import API
    # -------------------------------------------------------------------------
    def call_ccopen(self, source: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Open a computational chemistry file and return parser handle.

        Parameters:
            source: File path, file-like object, or supported input.
            *args: Forwarded to cclib.io.ccio.ccopen.
            **kwargs: Forwarded keyword arguments to ccopen.

        Returns:
            dict: status + parser handle under 'result'.
        """
        try:
            fn = self._get_callable("cclib.io.ccio", "ccopen")
            result = fn(source, *args, **kwargs)
            return self._ok({"result": result}, "ccopen executed")
        except Exception as exc:
            return self._err(
                "Unable to open input via import mode.",
                hint="Verify input path and required parser dependencies.",
                error=exc,
            )

    def call_ccread(self, source: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Parse a file and return cclib data object.

        Parameters:
            source: File path, file-like object, or supported input.
            *args: Forwarded positional arguments to cclib.io.ccio.ccread.
            **kwargs: Forwarded keyword arguments to ccread.

        Returns:
            dict: status + parsed data under 'result'.
        """
        try:
            fn = self._get_callable("cclib.io.ccio", "ccread")
            result = fn(source, *args, **kwargs)
            return self._ok({"result": result}, "ccread executed")
        except Exception as exc:
            return self._err(
                "Unable to parse input via import mode.",
                hint="Check file format support and install core dependencies: numpy, scipy, periodictable, packaging.",
                error=exc,
            )

    def call_ccwrite(self, ccobj: Any, outputtype: Optional[str] = None, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Convert cclib object to another output format.

        Parameters:
            ccobj: Parsed cclib data object.
            outputtype: Target format (e.g., cjson, xyz, molden, wfx).
            *args: Forwarded positional arguments.
            **kwargs: Forwarded keyword arguments.

        Returns:
            dict: status + converted content/path under 'result'.
        """
        try:
            fn = self._get_callable("cclib.io.ccio", "ccwrite")
            result = fn(ccobj, outputtype=outputtype, *args, **kwargs)
            return self._ok({"result": result}, "ccwrite executed")
        except Exception as exc:
            return self._err(
                "Unable to write converted output via import mode.",
                hint="Confirm outputtype is supported and writer dependencies are available.",
                error=exc,
            )

    # -------------------------------------------------------------------------
    # I/O class instance methods
    # -------------------------------------------------------------------------
    def instance_CJSON(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create cclib.io.cjsonreader.CJSON instance.

        Parameters:
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: status + instance under 'result'.
        """
        try:
            cls = self._get_callable("cclib.io.cjsonreader", "CJSON")
            return self._ok({"result": cls(*args, **kwargs)}, "CJSON instance created")
        except Exception as exc:
            return self._err("Failed to create CJSON reader instance.", hint="Check constructor arguments.", error=exc)

    def instance_CJSONWriter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create cclib.io.cjsonwriter.CJSON instance (writer-side API).

        Parameters:
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._get_callable("cclib.io.cjsonwriter", "CJSON")
            return self._ok({"result": cls(*args, **kwargs)}, "CJSON writer instance created")
        except Exception as exc:
            return self._err("Failed to create CJSON writer instance.", hint="Check constructor arguments.", error=exc)

    def instance_XYZ(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create cclib.io.xyzreader.XYZ instance.

        Parameters:
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._get_callable("cclib.io.xyzreader", "XYZ")
            return self._ok({"result": cls(*args, **kwargs)}, "XYZ reader instance created")
        except Exception as exc:
            return self._err("Failed to create XYZ reader instance.", hint="Check constructor arguments.", error=exc)

    def instance_XYZWriter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create cclib.io.xyzwriter.XYZ instance (writer-side API).

        Parameters:
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._get_callable("cclib.io.xyzwriter", "XYZ")
            return self._ok({"result": cls(*args, **kwargs)}, "XYZ writer instance created")
        except Exception as exc:
            return self._err("Failed to create XYZ writer instance.", hint="Check constructor arguments.", error=exc)

    def instance_MOLDEN(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create cclib.io.moldenwriter.MOLDEN instance.

        Parameters:
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._get_callable("cclib.io.moldenwriter", "MOLDEN")
            return self._ok({"result": cls(*args, **kwargs)}, "MOLDEN writer instance created")
        except Exception as exc:
            return self._err("Failed to create MOLDEN writer instance.", hint="Check constructor arguments.", error=exc)

    def instance_WFXWriter(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create cclib.io.wfxwriter.WFXWriter instance.

        Parameters:
            *args: Constructor positional args.
            **kwargs: Constructor keyword args.

        Returns:
            dict: status + instance.
        """
        try:
            cls = self._get_callable("cclib.io.wfxwriter", "WFXWriter")
            return self._ok({"result": cls(*args, **kwargs)}, "WFXWriter instance created")
        except Exception as exc:
            return self._err("Failed to create WFXWriter instance.", hint="Check constructor arguments.", error=exc)

    # -------------------------------------------------------------------------
    # CLI fallback guidance
    # -------------------------------------------------------------------------
    def cli_ccget(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run cclib ccget CLI entrypoint function if available.

        Parameters:
            argv: Optional argument list to pass to main().

        Returns:
            dict: status + execution result. If import-call unsupported, returns actionable fallback guidance.
        """
        try:
            fn = self._get_callable("cclib.scripts.ccget", "ccget")
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "ccget executed")
        except Exception as exc:
            return self._err(
                "ccget import execution failed.",
                hint="Fallback: run `python -m cclib.scripts.ccget --help` from project root.",
                error=exc,
            )

    def cli_ccwrite(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run cclib ccwrite CLI entrypoint function if available.

        Parameters:
            argv: Optional argument list to pass.

        Returns:
            dict: status + execution result or fallback guidance.
        """
        try:
            fn = self._get_callable("cclib.scripts.ccwrite", "ccwrite")
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "ccwrite CLI executed")
        except Exception as exc:
            return self._err(
                "ccwrite import execution failed.",
                hint="Fallback: run `python -m cclib.scripts.ccwrite --help` from project root.",
                error=exc,
            )

    def cli_ccframe(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run cclib ccframe CLI entrypoint function if available.

        Parameters:
            argv: Optional argument list to pass.

        Returns:
            dict: status + execution result or fallback guidance.
        """
        try:
            fn = self._get_callable("cclib.scripts.ccframe", "ccframe")
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "ccframe CLI executed")
        except Exception as exc:
            return self._err(
                "ccframe import execution failed.",
                hint="Fallback: run `python -m cclib.scripts.ccframe --help` from project root.",
                error=exc,
            )

    def cli_cda(self, argv: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run cclib cda CLI entrypoint function if available.

        Parameters:
            argv: Optional argument list to pass.

        Returns:
            dict: status + execution result or fallback guidance.
        """
        try:
            fn = self._get_callable("cclib.scripts.cda", "cda")
            result = fn(argv) if argv is not None else fn()
            return self._ok({"result": result}, "cda CLI executed")
        except Exception as exc:
            return self._err(
                "cda import execution failed.",
                hint="Fallback: run `python -m cclib.scripts.cda --help` from project root.",
                error=exc,
            )