import os
import sys
from typing import Any, Dict, Optional, Tuple

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    Import-mode adapter for the atomman repository.

    This adapter prioritizes direct imports from the local source tree and provides
    structured, unified responses for all operations. It covers key capabilities
    identified in analysis:
      - Unified loading dispatcher
      - Unified dumping dispatcher
      - Unit conversion helper functions

    Return format for all public methods:
      {
        "status": "success" | "error",
        "mode": "import" | "fallback",
        "data": ...,
        "message": "...",
        "error": "...",       # only for error
        "guidance": "..."     # actionable hint on errors
      }
    """

    # -------------------------------------------------------------------------
    # Lifecycle / Module Management
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._imports: Dict[str, Any] = {}
        self._initialize_imports()

    def _initialize_imports(self) -> None:
        """
        Attempt to import all identified atomman functions.

        Imports are performed from full package paths derived from the analysis:
          - atomman.load.__init__.load
          - atomman.dump.__init__.dump
          - atomman.unitconvert.unitconvert.{set_in_units,get_in_units,value_unit}
        """
        try:
            from atomman.load import load as atomman_load
            self._imports["load"] = atomman_load
        except Exception:
            self._imports["load"] = None

        try:
            from atomman.dump import dump as atomman_dump
            self._imports["dump"] = atomman_dump
        except Exception:
            self._imports["dump"] = None

        try:
            from atomman.unitconvert import set_in_units as uc_set_in_units
            from atomman.unitconvert import get_in_units as uc_get_in_units
            from atomman.unitconvert import value_unit as uc_value_unit
            self._imports["set_in_units"] = uc_set_in_units
            self._imports["get_in_units"] = uc_get_in_units
            self._imports["value_unit"] = uc_value_unit
        except Exception:
            self._imports["set_in_units"] = None
            self._imports["get_in_units"] = None
            self._imports["value_unit"] = None

        if not all(v is not None for v in self._imports.values()):
            self.mode = "fallback"

    def _ok(self, data: Any = None, message: str = "Operation completed.") -> Dict[str, Any]:
        return {
            "status": "success",
            "mode": self.mode,
            "data": data,
            "message": message,
        }

    def _err(self, error: Exception, guidance: str) -> Dict[str, Any]:
        return {
            "status": "error",
            "mode": self.mode,
            "data": None,
            "message": "Operation failed.",
            "error": str(error),
            "guidance": guidance,
        }

    def health_check(self) -> Dict[str, Any]:
        """
        Report adapter readiness and import availability.

        Returns:
            dict: Unified status with per-function import availability.
        """
        availability = {k: v is not None for k, v in self._imports.items()}
        return self._ok(
            data={"imports": availability, "mode": self.mode},
            message="Health check completed.",
        )

    # -------------------------------------------------------------------------
    # Function Module: atomman.load.__init__.load
    # -------------------------------------------------------------------------
    def call_load(self, style: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call atomman's unified loader dispatcher.

        Parameters:
            style (str): Loader style/format key (e.g., 'atom_data', 'poscar', 'cif', etc.).
            *args: Positional arguments forwarded to atomman.load.load.
            **kwargs: Keyword arguments forwarded to atomman.load.load.

        Returns:
            dict: Unified response containing loaded object in `data` on success.

        Guidance:
            - Ensure format-specific dependencies are installed (e.g., pymatgen, ase, spglib).
            - Verify the provided style matches available atomman loader modules.
        """
        fn = self._imports.get("load")
        if fn is None:
            return self._err(
                RuntimeError("Import for atomman.load.load is unavailable."),
                "Verify local source checkout under 'source/atomman' and install required dependencies from requirements.txt.",
            )
        try:
            result = fn(style, *args, **kwargs)
            return self._ok(data=result, message="Load operation completed.")
        except Exception as e:
            return self._err(
                e,
                "Check style name, input file path/content, and optional dependency packages for the selected format.",
            )

    # -------------------------------------------------------------------------
    # Function Module: atomman.dump.__init__.dump
    # -------------------------------------------------------------------------
    def call_dump(self, style: str, system: Any, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call atomman's unified dump/export dispatcher.

        Parameters:
            style (str): Dump style/format key (e.g., 'atom_data', 'poscar', 'pdb', etc.).
            system (Any): Atomman System-like object to export.
            *args: Positional arguments forwarded to atomman.dump.dump.
            **kwargs: Keyword arguments forwarded to atomman.dump.dump.

        Returns:
            dict: Unified response containing dumped representation/path/obj in `data`.

        Guidance:
            - Validate `system` object compatibility with selected dump style.
            - Confirm optional format dependencies are installed.
        """
        fn = self._imports.get("dump")
        if fn is None:
            return self._err(
                RuntimeError("Import for atomman.dump.dump is unavailable."),
                "Verify local source checkout under 'source/atomman' and install required dependencies from requirements.txt.",
            )
        try:
            result = fn(style, system, *args, **kwargs)
            return self._ok(data=result, message="Dump operation completed.")
        except Exception as e:
            return self._err(
                e,
                "Check style name, provided system object, destination arguments, and optional format dependencies.",
            )

    # -------------------------------------------------------------------------
    # Function Module: atomman.unitconvert.unitconvert
    # -------------------------------------------------------------------------
    def call_set_in_units(self, value: Any, units: str) -> Dict[str, Any]:
        """
        Convert a value from working units into specified physical units.

        Parameters:
            value (Any): Numeric value/array-like to convert.
            units (str): Target units string recognized by atomman/numericalunits.

        Returns:
            dict: Converted value in `data`.
        """
        fn = self._imports.get("set_in_units")
        if fn is None:
            return self._err(
                RuntimeError("Import for atomman.unitconvert.set_in_units is unavailable."),
                "Install required dependency 'numericalunits' and ensure unitconvert module is accessible in source.",
            )
        try:
            result = fn(value, units)
            return self._ok(data=result, message="set_in_units completed.")
        except Exception as e:
            return self._err(
                e,
                "Verify units string validity and ensure value is numeric or array-like.",
            )

    def call_get_in_units(self, value: Any, units: str) -> Dict[str, Any]:
        """
        Convert a value expressed in specified units into atomman's working units.

        Parameters:
            value (Any): Numeric value/array-like to convert.
            units (str): Source units string recognized by atomman/numericalunits.

        Returns:
            dict: Converted value in working units in `data`.
        """
        fn = self._imports.get("get_in_units")
        if fn is None:
            return self._err(
                RuntimeError("Import for atomman.unitconvert.get_in_units is unavailable."),
                "Install required dependency 'numericalunits' and ensure unitconvert module is accessible in source.",
            )
        try:
            result = fn(value, units)
            return self._ok(data=result, message="get_in_units completed.")
        except Exception as e:
            return self._err(
                e,
                "Verify units string validity and ensure value is numeric or array-like.",
            )

    def call_value_unit(self, value: Any, units: str) -> Dict[str, Any]:
        """
        Package a numeric value with units using atomman's value-unit utility.

        Parameters:
            value (Any): Numeric value/array-like.
            units (str): Units label/string.

        Returns:
            dict: Value-unit representation in `data`.
        """
        fn = self._imports.get("value_unit")
        if fn is None:
            return self._err(
                RuntimeError("Import for atomman.unitconvert.value_unit is unavailable."),
                "Install required dependency 'numericalunits' and ensure unitconvert module is accessible in source.",
            )
        try:
            result = fn(value, units)
            return self._ok(data=result, message="value_unit completed.")
        except Exception as e:
            return self._err(
                e,
                "Ensure value is serializable/numeric and units string is valid.",
            )