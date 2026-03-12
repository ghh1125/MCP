import os
import sys
import traceback
import importlib
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
if source_path not in sys.path:
    sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode MCP adapter for the ObsPy repository.

    This adapter prioritizes direct module import/use and provides structured
    fallback guidance when imports or calls fail.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Optional[Any]] = {}
        self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _result(self, status: str, **kwargs: Any) -> Dict[str, Any]:
        payload = {"status": status}
        payload.update(kwargs)
        return payload

    def _safe_import(self, module_path: str) -> Optional[Any]:
        try:
            mod = importlib.import_module(module_path)
            return mod
        except Exception:
            return None

    def _load_modules(self) -> None:
        module_paths = [
            "obspy",
            "obspy.scripts.print",
            "obspy.scripts.flinnengdahl",
            "obspy.scripts.reftekrescue",
            "obspy.scripts.runtests",
            "obspy.imaging.scripts.scan",
            "obspy.imaging.scripts.plot",
            "obspy.imaging.scripts.mopad",
            "obspy.clients.fdsn.client",
            "obspy.clients.filesystem.sds",
            "obspy.clients.seedlink.basic_client",
            "obspy.signal.filter",
            "obspy.signal.trigger",
            "obspy.geodetics.base",
            "obspy.taup",
        ]
        for p in module_paths:
            self._modules[p] = self._safe_import(p)

    def _get_module(self, module_path: str) -> Dict[str, Any]:
        mod = self._modules.get(module_path)
        if mod is None:
            mod = self._safe_import(module_path)
            self._modules[module_path] = mod
        if mod is None:
            return self._result(
                "error",
                error=f"Failed to import module '{module_path}'.",
                guidance=(
                    "Ensure the repository source is available under the configured "
                    "source path and required dependencies are installed."
                ),
            )
        return self._result("success", module=mod)

    def _instantiate(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod_res = self._get_module(module_path)
        if mod_res["status"] != "success":
            return mod_res
        try:
            cls = getattr(mod_res["module"], class_name)
            instance = cls(*args, **kwargs)
            return self._result("success", instance=instance)
        except AttributeError:
            return self._result(
                "error",
                error=f"Class '{class_name}' not found in module '{module_path}'.",
                guidance="Verify class name against the repository version.",
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to instantiate '{class_name}': {exc}",
                traceback=traceback.format_exc(),
                guidance="Check constructor arguments and dependency availability.",
            )

    def _call(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        mod_res = self._get_module(module_path)
        if mod_res["status"] != "success":
            return mod_res
        try:
            fn = getattr(mod_res["module"], function_name)
            result = fn(*args, **kwargs)
            return self._result("success", result=result)
        except AttributeError:
            return self._result(
                "error",
                error=f"Function '{function_name}' not found in module '{module_path}'.",
                guidance="Verify function name against the repository version.",
            )
        except Exception as exc:
            return self._result(
                "error",
                error=f"Failed to execute '{function_name}': {exc}",
                traceback=traceback.format_exc(),
                guidance="Validate inputs and runtime environment.",
            )

    # -------------------------------------------------------------------------
    # Status and diagnostics
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Check import readiness of key ObsPy modules and return diagnostics.
        """
        loaded = {k: (v is not None) for k, v in self._modules.items()}
        ok = all(loaded.values())
        return self._result(
            "success" if ok else "partial",
            mode=self.mode,
            source_path=source_path,
            modules=loaded,
            guidance=(
                "If partial, install missing dependencies: numpy, scipy, matplotlib, "
                "lxml, sqlalchemy, requests (plus optional extras as needed)."
            ),
        )

    # -------------------------------------------------------------------------
    # Core import-oriented wrappers (classes)
    # -------------------------------------------------------------------------
    def create_fdsn_client(self, base_url: str = "IRIS", user: Optional[str] = None, password: Optional[str] = None,
                           **kwargs: Any) -> Dict[str, Any]:
        """
        Create obspy.clients.fdsn.client.Client instance.

        Parameters:
        - base_url: FDSN service alias or URL.
        - user/password: Optional credentials.
        - kwargs: Additional constructor args accepted by ObsPy.
        """
        return self._instantiate(
            "obspy.clients.fdsn.client",
            "Client",
            base_url,
            user=user,
            password=password,
            **kwargs,
        )

    def create_sds_client(self, sds_root: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Create obspy.clients.filesystem.sds.Client instance.

        Parameters:
        - sds_root: Root directory of SDS archive.
        - kwargs: Additional constructor args.
        """
        return self._instantiate("obspy.clients.filesystem.sds", "Client", sds_root, **kwargs)

    def create_seedlink_basic_client(self, server: str, port: int = 18000, **kwargs: Any) -> Dict[str, Any]:
        """
        Create obspy.clients.seedlink.basic_client.Client instance.

        Parameters:
        - server: SeedLink server hostname.
        - port: SeedLink server port.
        - kwargs: Additional constructor args.
        """
        return self._instantiate("obspy.clients.seedlink.basic_client", "Client", server, port=port, **kwargs)

    # -------------------------------------------------------------------------
    # Core import-oriented wrappers (functions)
    # -------------------------------------------------------------------------
    def call_obspy_read(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call obspy.read() for waveform loading.
        """
        return self._call("obspy", "read", *args, **kwargs)

    def call_obspy_read_inventory(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call obspy.read_inventory() for station metadata loading.
        """
        return self._call("obspy", "read_inventory", *args, **kwargs)

    def call_obspy_read_events(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call obspy.read_events() for event catalog loading.
        """
        return self._call("obspy", "read_events", *args, **kwargs)

    def call_geodetics_locations2degrees(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call obspy.geodetics.base.locations2degrees().
        """
        return self._call("obspy.geodetics.base", "locations2degrees", *args, **kwargs)

    def call_geodetics_gps2dist_azimuth(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call obspy.geodetics.base.gps2dist_azimuth().
        """
        return self._call("obspy.geodetics.base", "gps2dist_azimuth", *args, **kwargs)

    def create_taup_model(self, model: str = "iasp91") -> Dict[str, Any]:
        """
        Create obspy.taup.TauPyModel instance.

        Parameters:
        - model: TauP Earth model name.
        """
        return self._instantiate("obspy.taup", "TauPyModel", model=model)

    # -------------------------------------------------------------------------
    # CLI module adapters (import-mode fallback for command workflows)
    # -------------------------------------------------------------------------
    def call_cli_module_main(self, module_path: str, argv: Optional[list] = None) -> Dict[str, Any]:
        """
        Execute a CLI module main() in import mode.

        Parameters:
        - module_path: Full module path (e.g., 'obspy.scripts.print').
        - argv: Optional argument list to inject as sys.argv[1:].
        """
        mod_res = self._get_module(module_path)
        if mod_res["status"] != "success":
            return mod_res
        mod = mod_res["module"]
        if not hasattr(mod, "main"):
            return self._result(
                "error",
                error=f"Module '{module_path}' does not expose a main() function.",
                guidance="Use direct API methods where possible or verify module entry behavior.",
            )
        old_argv = sys.argv[:]
        try:
            if argv is not None:
                sys.argv = [module_path] + list(argv)
            out = mod.main()
            return self._result("success", result=out)
        except Exception as exc:
            return self._result(
                "error",
                error=f"CLI main execution failed for '{module_path}': {exc}",
                traceback=traceback.format_exc(),
                guidance="Check command arguments and local data paths.",
            )
        finally:
            sys.argv = old_argv

    def run_obspy_print(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.scripts.print", argv=argv)

    def run_obspy_flinn_engdahl(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.scripts.flinnengdahl", argv=argv)

    def run_obspy_reftek_rescue(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.scripts.reftekrescue", argv=argv)

    def run_obspy_scan(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.imaging.scripts.scan", argv=argv)

    def run_obspy_plot(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.imaging.scripts.plot", argv=argv)

    def run_obspy_mopad(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.imaging.scripts.mopad", argv=argv)

    def run_obspy_runtests(self, argv: Optional[list] = None) -> Dict[str, Any]:
        return self.call_cli_module_main("obspy.scripts.runtests", argv=argv)