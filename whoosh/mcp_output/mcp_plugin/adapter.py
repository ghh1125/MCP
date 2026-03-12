import os
import sys
import traceback
import importlib
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class Adapter:
    """
    MCP Import Mode Adapter for the Whoosh repository.

    This adapter focuses on safe import-mode integration with practical, high-value
    entry points inferred from analysis:
    - Core package import and version metadata
    - Index lifecycle helpers
    - Query parsing and search execution
    - Script module loading for maintenance utilities
    - Generic module/function/class access for extensibility
    """

    # -------------------------------------------------------------------------
    # Initialization / State
    # -------------------------------------------------------------------------
    def __init__(self) -> None:
        self.mode = "import"
        self._modules: Dict[str, Any] = {}
        self._import_error: Optional[str] = None
        self._bootstrap()

    def _bootstrap(self) -> None:
        try:
            self._modules["whoosh"] = importlib.import_module("whoosh")
            self._modules["whoosh.index"] = importlib.import_module("whoosh.index")
            self._modules["whoosh.fields"] = importlib.import_module("whoosh.fields")
            self._modules["whoosh.qparser"] = importlib.import_module("whoosh.qparser")
            self._modules["whoosh.query"] = importlib.import_module("whoosh.query")
            self._modules["whoosh.scoring"] = importlib.import_module("whoosh.scoring")
            self._modules["whoosh.sorting"] = importlib.import_module("whoosh.sorting")
            self._modules["whoosh.searching"] = importlib.import_module("whoosh.searching")
        except Exception as exc:
            self._import_error = (
                f"Import mode initialization failed. Ensure repository source exists at "
                f"'{source_path}' and contains the 'whoosh' package. Details: {exc}"
            )

    def _ok(self, data: Any = None, message: str = "success") -> Dict[str, Any]:
        return {"status": "success", "mode": self.mode, "message": message, "data": data}

    def _err(self, message: str, error: Optional[Exception] = None) -> Dict[str, Any]:
        payload = {"status": "error", "mode": self.mode, "message": message}
        if error is not None:
            payload["error"] = str(error)
            payload["traceback"] = traceback.format_exc()
        if self._import_error:
            payload["guidance"] = self._import_error
        return payload

    def _fallback(self, action: str) -> Dict[str, Any]:
        msg = (
            f"Cannot execute '{action}' in import mode because Whoosh imports are unavailable. "
            f"Verify local repository sync and source path configuration."
        )
        return self._err(msg)

    # -------------------------------------------------------------------------
    # Health / Metadata
    # -------------------------------------------------------------------------
    def health_check(self) -> Dict[str, Any]:
        """
        Validate adapter readiness and import availability.

        Returns:
            dict: Unified status payload with loaded module names and version when available.
        """
        if self._import_error:
            return self._fallback("health_check")
        try:
            whoosh_mod = self._modules["whoosh"]
            version = getattr(whoosh_mod, "__version__", "unknown")
            return self._ok(
                data={"version": version, "loaded_modules": sorted(self._modules.keys())},
                message="Adapter is ready in import mode.",
            )
        except Exception as exc:
            return self._err("Health check failed unexpectedly.", exc)

    # -------------------------------------------------------------------------
    # Module Management
    # -------------------------------------------------------------------------
    def load_module(self, module_path: str) -> Dict[str, Any]:
        """
        Dynamically import and cache a module from the repository.

        Args:
            module_path: Full module path, e.g. 'whoosh.analysis' or 'scripts.make_checkpoint'.

        Returns:
            dict: Unified status payload with module metadata.
        """
        try:
            mod = importlib.import_module(module_path)
            self._modules[module_path] = mod
            return self._ok(
                data={"module": module_path, "file": getattr(mod, "__file__", None)},
                message=f"Module '{module_path}' loaded.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to import module '{module_path}'. Confirm path and repository contents.",
                exc,
            )

    def list_loaded_modules(self) -> Dict[str, Any]:
        """
        List modules currently cached by the adapter.

        Returns:
            dict: Unified status payload with loaded module names.
        """
        return self._ok(data={"modules": sorted(self._modules.keys())})

    # -------------------------------------------------------------------------
    # Script Utilities (identified CLI-like modules)
    # -------------------------------------------------------------------------
    def load_make_checkpoint_script(self) -> Dict[str, Any]:
        """
        Import scripts.make_checkpoint module.

        Returns:
            dict: Unified status payload for script module import.
        """
        return self.load_module("scripts.make_checkpoint")

    def load_read_checkpoint_script(self) -> Dict[str, Any]:
        """
        Import scripts.read_checkpoint module.

        Returns:
            dict: Unified status payload for script module import.
        """
        return self.load_module("scripts.read_checkpoint")

    # -------------------------------------------------------------------------
    # Index / Schema Operations
    # -------------------------------------------------------------------------
    def create_schema_class(self, **field_definitions: Any) -> Dict[str, Any]:
        """
        Instantiate whoosh.fields.Schema with provided field definitions.

        Args:
            **field_definitions: Keyword mapping of field names to whoosh field objects
                (e.g., TEXT(stored=True), ID(unique=True), NUMERIC()).

        Returns:
            dict: Unified status payload containing the schema instance.
        """
        if self._import_error:
            return self._fallback("create_schema_class")
        try:
            Schema = getattr(self._modules["whoosh.fields"], "Schema")
            schema = Schema(**field_definitions)
            return self._ok(data={"schema": schema}, message="Schema instance created.")
        except Exception as exc:
            return self._err(
                "Failed to create schema. Ensure field objects are valid Whoosh field instances.",
                exc,
            )

    def call_create_in(self, dirname: str, schema: Any, indexname: Optional[str] = None) -> Dict[str, Any]:
        """
        Call whoosh.index.create_in to create an index in a directory.

        Args:
            dirname: Target directory path.
            schema: Whoosh Schema instance.
            indexname: Optional index file name.

        Returns:
            dict: Unified status payload with created index object.
        """
        if self._import_error:
            return self._fallback("call_create_in")
        try:
            create_in = getattr(self._modules["whoosh.index"], "create_in")
            ix = create_in(dirname, schema, indexname=indexname) if indexname else create_in(dirname, schema)
            return self._ok(data={"index": ix}, message="Index created successfully.")
        except Exception as exc:
            return self._err(
                "Failed to create index. Check directory permissions and schema validity.",
                exc,
            )

    def call_open_dir(self, dirname: str, indexname: Optional[str] = None, readonly: bool = False) -> Dict[str, Any]:
        """
        Call whoosh.index.open_dir to open an existing index.

        Args:
            dirname: Directory containing index files.
            indexname: Optional index file name.
            readonly: Open in read-only mode when supported.

        Returns:
            dict: Unified status payload with opened index object.
        """
        if self._import_error:
            return self._fallback("call_open_dir")
        try:
            open_dir = getattr(self._modules["whoosh.index"], "open_dir")
            kwargs = {"readonly": readonly}
            if indexname is not None:
                kwargs["indexname"] = indexname
            ix = open_dir(dirname, **kwargs)
            return self._ok(data={"index": ix}, message="Index opened successfully.")
        except Exception as exc:
            return self._err(
                "Failed to open index directory. Ensure path exists and index files are valid.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Query Parsing / Search
    # -------------------------------------------------------------------------
    def create_query_parser_class(self, default_field: str, schema: Any, group: Any = None) -> Dict[str, Any]:
        """
        Instantiate whoosh.qparser.QueryParser.

        Args:
            default_field: Default field name used by the parser.
            schema: Whoosh schema instance.
            group: Optional parser grouping strategy.

        Returns:
            dict: Unified status payload with parser instance.
        """
        if self._import_error:
            return self._fallback("create_query_parser_class")
        try:
            QueryParser = getattr(self._modules["whoosh.qparser"], "QueryParser")
            parser = QueryParser(default_field, schema, group=group) if group else QueryParser(default_field, schema)
            return self._ok(data={"parser": parser}, message="QueryParser instance created.")
        except Exception as exc:
            return self._err(
                "Failed to create QueryParser. Verify default field and schema.",
                exc,
            )

    def call_parse_query(self, parser: Any, query_text: str) -> Dict[str, Any]:
        """
        Parse query text using a QueryParser instance.

        Args:
            parser: QueryParser instance.
            query_text: User query string.

        Returns:
            dict: Unified status payload with parsed query object.
        """
        try:
            q = parser.parse(query_text)
            return self._ok(data={"query": q}, message="Query parsed successfully.")
        except Exception as exc:
            return self._err(
                "Failed to parse query text. Validate parser configuration and query syntax.",
                exc,
            )

    def call_search(self, index_obj: Any, query_obj: Any, limit: int = 10, sortedby: Any = None) -> Dict[str, Any]:
        """
        Execute search against an index.

        Args:
            index_obj: Whoosh index object.
            query_obj: Parsed query object.
            limit: Maximum number of results.
            sortedby: Optional sort configuration.

        Returns:
            dict: Unified status payload with result count and raw result object.
        """
        try:
            with index_obj.searcher() as searcher:
                results = searcher.search(query_obj, limit=limit, sortedby=sortedby)
                return self._ok(
                    data={"results": results, "count": len(results)},
                    message="Search executed successfully.",
                )
        except Exception as exc:
            return self._err(
                "Search failed. Ensure index, query object, and sorting configuration are valid.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Generic Function/Class Access (extensible coverage)
    # -------------------------------------------------------------------------
    def create_instance(self, module_path: str, class_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Create an instance from an arbitrary class in a repository module.

        Args:
            module_path: Full module path.
            class_name: Class name to instantiate.
            *args: Positional constructor args.
            **kwargs: Keyword constructor args.

        Returns:
            dict: Unified status payload with created instance.
        """
        try:
            mod = self._modules.get(module_path) or importlib.import_module(module_path)
            self._modules[module_path] = mod
            cls = getattr(mod, class_name)
            instance = cls(*args, **kwargs)
            return self._ok(
                data={"instance": instance, "module": module_path, "class": class_name},
                message="Class instance created successfully.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to instantiate '{class_name}' from '{module_path}'. Confirm constructor arguments.",
                exc,
            )

    def call_function(self, module_path: str, function_name: str, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """
        Call an arbitrary function from a repository module.

        Args:
            module_path: Full module path.
            function_name: Target function name.
            *args: Positional call arguments.
            **kwargs: Keyword call arguments.

        Returns:
            dict: Unified status payload with function output.
        """
        try:
            mod = self._modules.get(module_path) or importlib.import_module(module_path)
            self._modules[module_path] = mod
            fn = getattr(mod, function_name)
            output = fn(*args, **kwargs)
            return self._ok(
                data={"result": output, "module": module_path, "function": function_name},
                message="Function executed successfully.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to call '{function_name}' from '{module_path}'. Verify function signature and arguments.",
                exc,
            )

    # -------------------------------------------------------------------------
    # Discovery Helpers
    # -------------------------------------------------------------------------
    def inspect_module_symbols(self, module_path: str, include_private: bool = False) -> Dict[str, Any]:
        """
        Inspect module symbols for discovery and adapter extension.

        Args:
            module_path: Full module path to inspect.
            include_private: Include private names starting with underscore.

        Returns:
            dict: Unified status payload with symbol listing.
        """
        try:
            mod = self._modules.get(module_path) or importlib.import_module(module_path)
            self._modules[module_path] = mod
            names: List[str] = dir(mod)
            if not include_private:
                names = [n for n in names if not n.startswith("_")]
            return self._ok(
                data={"module": module_path, "symbols": sorted(names)},
                message="Module symbols inspected successfully.",
            )
        except Exception as exc:
            return self._err(
                f"Failed to inspect module '{module_path}'. Confirm module path is correct.",
                exc,
            )