import os
import sys
import traceback
import importlib
import inspect
from typing import Any, Dict, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the autodE repository.

    This adapter attempts to import and expose key classes/functions from the
    repository using direct Python imports. If import fails, it degrades
    gracefully with actionable error guidance.
    """

    def __init__(self) -> None:
        self.mode = "import"
        self.repo_name = "autodE"
        self.repo_url = "https://github.com/duartegroup/autodE"
        self._modules: Dict[str, Any] = {}
        self._init_result = self._load_modules()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _ok(self, data: Optional[Dict[str, Any]] = None, message: str = "success") -> Dict[str, Any]:
        payload = {"status": "ok", "mode": self.mode, "message": message}
        if data:
            payload.update(data)
        return payload

    def _error(self, message: str, exc: Optional[Exception] = None, guidance: Optional[str] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if guidance:
            payload["guidance"] = guidance
        if exc is not None:
            payload["error_type"] = exc.__class__.__name__
            payload["error"] = str(exc)
            payload["traceback"] = traceback.format_exc()
        return payload

    def _import_module(self, module_path: str) -> Dict[str, Any]:
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return self._ok({"module": module_path}, f"Imported module: {module_path}")
        except Exception as exc:
            return self._error(
                f"Failed to import module: {module_path}",
                exc=exc,
                guidance=(
                    "Ensure required dependencies are installed (numpy, scipy, networkx). "
                    "Optional features may need rdkit, matplotlib, cclib and external binaries "
                    "(xtb, orca, gaussian, qchem, nwchem, mopac)."
                ),
            )

    def _get_obj(self, module_path: str, attr_name: str) -> Any:
        if module_path not in self._modules:
            imported = self._import_module(module_path)
            if imported["status"] != "ok":
                raise ImportError(imported["message"])
        mod = self._modules[module_path]
        return getattr(mod, attr_name)

    def _load_modules(self) -> Dict[str, Any]:
        module_candidates = [
            "autode",
            "autode.atoms",
            "autode.species.molecule",
            "autode.species.complex",
            "autode.reactions.reaction",
            "autode.reactions.multistep",
            "autode.transition_states.transition_state",
            "autode.transition_states.locate_tss",
            "autode.conformers.conformer",
            "autode.conformers.conformers",
            "autode.calculations.calculation",
            "autode.pes.relaxed",
            "autode.pes.unrelaxed",
            "autode.path.path",
            "autode.path.interpolation",
            "autode.opt.optimisers.base",
            "autode.smiles.smiles",
            "autode.input_output",
            "autode.methods",
            "autode.config",
        ]

        imported = {}
        failed = {}
        for m in module_candidates:
            res = self._import_module(m)
            if res["status"] == "ok":
                imported[m] = True
            else:
                failed[m] = res["message"]

        if failed:
            return self._error(
                "Module preload completed with partial failures",
                guidance="You can still call available methods; unavailable modules will return structured errors.",
            ) | {"imported_count": len(imported), "failed": failed}
        return self._ok({"imported_count": len(imported)}, "All key modules imported")

    # -------------------------------------------------------------------------
    # Health / status
    # -------------------------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        """
        Return adapter initialization and import status.
        """
        return self._ok(
            data={
                "repo": self.repo_name,
                "repo_url": self.repo_url,
                "init_result": self._init_result,
                "loaded_modules": sorted(list(self._modules.keys())),
            },
            message="Adapter status retrieved",
        )

    # -------------------------------------------------------------------------
    # Generic reflection-based utilities
    # -------------------------------------------------------------------------
    def list_module_members(self, module_path: str, include_private: bool = False) -> Dict[str, Any]:
        """
        List attributes in a module.

        Parameters:
            module_path: Full module path, e.g., 'autode.species.molecule'
            include_private: Whether to include names starting with '_'
        """
        try:
            self._import_module(module_path)
            mod = self._modules[module_path]
            names = dir(mod)
            if not include_private:
                names = [n for n in names if not n.startswith("_")]
            return self._ok({"module": module_path, "members": names}, "Module members listed")
        except Exception as exc:
            return self._error("Could not list module members", exc=exc)

    def call_module_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call any function from any module dynamically.

        Parameters:
            module_path: Full module path.
            function_name: Function name in module.
            *args, **kwargs: Arguments for the target function.
        """
        try:
            fn = self._get_obj(module_path, function_name)
            if not callable(fn):
                return self._error(f"Target '{function_name}' is not callable")
            result = fn(*args, **kwargs)
            return self._ok({"result": result}, f"Function '{function_name}' executed")
        except Exception as exc:
            return self._error(
                f"Failed to execute function '{function_name}' from '{module_path}'",
                exc=exc,
                guidance="Verify function name and arguments using list_module_members.",
            )

    def create_class_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Instantiate any class dynamically.

        Parameters:
            module_path: Full module path.
            class_name: Class name in module.
            *args, **kwargs: Constructor args.
        """
        try:
            cls = self._get_obj(module_path, class_name)
            if not inspect.isclass(cls):
                return self._error(f"Target '{class_name}' is not a class")
            obj = cls(*args, **kwargs)
            return self._ok({"instance": obj}, f"Class '{class_name}' instantiated")
        except Exception as exc:
            return self._error(
                f"Failed to instantiate class '{class_name}' from '{module_path}'",
                exc=exc,
                guidance="Check constructor signature and required dependencies.",
            )

    # -------------------------------------------------------------------------
    # Dedicated class instance methods (high-value autodE objects)
    # -------------------------------------------------------------------------
    def create_atom(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.atoms", "Atom", *args, **kwargs)

    def create_atoms(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.atoms", "Atoms", *args, **kwargs)

    def create_molecule(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.species.molecule", "Molecule", *args, **kwargs)

    def create_complex(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.species.complex", "Complex", *args, **kwargs)

    def create_reaction(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.reactions.reaction", "Reaction", *args, **kwargs)

    def create_multistep_reaction(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.reactions.multistep", "MultiStepReaction", *args, **kwargs)

    def create_transition_state(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.transition_states.transition_state", "TransitionState", *args, **kwargs)

    def create_conformer(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.conformers.conformer", "Conformer", *args, **kwargs)

    def create_conformers(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.conformers.conformers", "Conformers", *args, **kwargs)

    def create_calculation(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.create_class_instance("autode.calculations.calculation", "Calculation", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Dedicated function call methods (common workflows)
    # -------------------------------------------------------------------------
    def smiles_to_molecule(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Convert/build molecule-like object from SMILES-related module functions.
        """
        try:
            # Try common names; fallback to dynamic guidance.
            for name in ("init_smiles", "smiles_to_molecule", "from_smiles"):
                try:
                    return self.call_module_function("autode.smiles.smiles", name, *args, **kwargs)
                except Exception:
                    continue
            return self._error(
                "No recognized SMILES conversion function found",
                guidance="Inspect autode.smiles.smiles with list_module_members to choose the correct function.",
            )
        except Exception as exc:
            return self._error("SMILES conversion failed", exc=exc)

    def locate_transition_state(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("autode.transition_states.locate_tss", "find_tss", *args, **kwargs)

    def read_xyz(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("autode.input_output", "xyz_file_to_atoms", *args, **kwargs)

    def get_hmethod(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("autode.methods", "get_hmethod", *args, **kwargs)

    def get_lmethod(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self.call_module_function("autode.methods", "get_lmethod", *args, **kwargs)

    # -------------------------------------------------------------------------
    # Config / environment helpers
    # -------------------------------------------------------------------------
    def get_config(self) -> Dict[str, Any]:
        """
        Return autode.config.Config object if available.
        """
        try:
            cfg = self._get_obj("autode.config", "Config")
            return self._ok({"config": cfg}, "Config retrieved")
        except Exception as exc:
            return self._error(
                "Failed to retrieve config",
                exc=exc,
                guidance="Ensure autode.config imports correctly in your environment.",
            )

    def check_dependencies(self) -> Dict[str, Any]:
        """
        Basic dependency probe based on LLM analysis.
        """
        required = ["numpy", "scipy", "networkx"]
        optional = ["rdkit", "matplotlib", "cclib"]
        external_bins = ["xtb", "orca", "g16", "qchem", "nwchem", "mopac"]

        req_status = {}
        opt_status = {}
        bin_status = {}

        for pkg in required:
            try:
                importlib.import_module(pkg)
                req_status[pkg] = True
            except Exception:
                req_status[pkg] = False

        for pkg in optional:
            try:
                importlib.import_module(pkg)
                opt_status[pkg] = True
            except Exception:
                opt_status[pkg] = False

        for b in external_bins:
            found = any(
                os.path.isfile(os.path.join(path, b)) or os.path.isfile(os.path.join(path, f"{b}.exe"))
                for path in os.environ.get("PATH", "").split(os.pathsep)
            )
            bin_status[b] = found

        return self._ok(
            {
                "required_python_packages": req_status,
                "optional_python_packages": opt_status,
                "external_binaries": bin_status,
            },
            "Dependency check completed",
        )