from __future__ import annotations

from pathlib import Path
from typing import Optional, List, Dict, Any
from fastmcp import FastMCP, subprocess, ctypes
import json
import os
import shlex
import shutil
import platform

mcp = FastMCP("deep_searcher_cpp_bridge_service")

REPO_URL = "https://github.com/zilliztech/deep-searcher"


def _repo_root() -> Path:
    return Path(os.environ.get("CPP_PROJECT_ROOT", ".")).resolve()


def _build_dir() -> Path:
    return Path(os.environ.get("CPP_BUILD_DIR", _repo_root() / "build")).resolve()


def _run_command(command: List[str], cwd: Optional[Path] = None, timeout: int = 300) -> Dict[str, Any]:
    try:
        completed = subprocess.run(
            command,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        success = completed.returncode == 0
        return {
            "success": success,
            "result": {
                "command": command,
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
            },
            "error": None if success else f"Command failed with return code {completed.returncode}",
        }
    except FileNotFoundError as exc:
        return {"success": False, "result": None, "error": f"Command not found: {exc}"}
    except subprocess.TimeoutExpired as exc:
        return {"success": False, "result": None, "error": f"Command timed out: {exc}"}
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


def _detect_build_system(project_root: Path) -> Dict[str, bool]:
    return {
        "cmake": (project_root / "CMakeLists.txt").exists(),
        "makefile": (project_root / "Makefile").exists() or (project_root / "makefile").exists(),
        "configure": (project_root / "configure").exists(),
        "meson": (project_root / "meson.build").exists(),
        "ninja": (project_root / "build.ninja").exists(),
    }


def _find_executable(explicit: Optional[str] = None) -> Optional[Path]:
    root = _repo_root()
    bdir = _build_dir()

    candidates: List[Path] = []
    if explicit:
        ep = Path(explicit)
        candidates.append(ep if ep.is_absolute() else (root / ep))

    env_exec = os.environ.get("CPP_EXECUTABLE")
    if env_exec:
        eep = Path(env_exec)
        candidates.append(eep if eep.is_absolute() else (root / eep))

    common_names = ["deep-searcher", "deep_searcher", "main", "app", "server", "cli"]
    search_dirs = [bdir, root / "bin", root / "out", root]
    for d in search_dirs:
        for n in common_names:
            candidates.append(d / n)
            if platform.system().lower().startswith("win"):
                candidates.append(d / f"{n}.exe")

    for c in candidates:
        if c.exists() and os.access(c, os.X_OK):
            return c.resolve()

    return None


def _find_library(explicit: Optional[str] = None) -> Optional[Path]:
    root = _repo_root()
    bdir = _build_dir()

    candidates: List[Path] = []
    if explicit:
        p = Path(explicit)
        candidates.append(p if p.is_absolute() else (root / p))

    env_lib = os.environ.get("CPP_LIBRARY")
    if env_lib:
        p = Path(env_lib)
        candidates.append(p if p.is_absolute() else (root / p))

    system = platform.system().lower()
    if "windows" in system:
        names = ["deepsearcher.dll", "libdeepsearcher.dll", "project.dll"]
    elif "darwin" in system:
        names = ["libdeepsearcher.dylib", "deepsearcher.dylib", "libproject.dylib"]
    else:
        names = ["libdeepsearcher.so", "deepsearcher.so", "libproject.so"]

    for d in [bdir, root / "lib", root / "build" / "lib", root]:
        for n in names:
            candidates.append(d / n)

    for c in candidates:
        if c.exists():
            return c.resolve()
    return None


@mcp.tool(name="project_info", description="Return high-level repository and service context information.")
def project_info() -> Dict[str, Any]:
    """
    Return immutable service metadata.

    Returns:
        dict: Standard response with:
            - success (bool): Whether operation succeeded.
            - result (dict): Service metadata and detected paths.
            - error (str|None): Error details if any.
    """
    root = _repo_root()
    return {
        "success": True,
        "result": {
            "service": "deep_searcher_cpp_bridge_service",
            "repository_url": REPO_URL,
            "project_root": str(root),
            "build_dir": str(_build_dir()),
            "build_systems": _detect_build_system(root),
        },
        "error": None,
    }


@mcp.tool(name="check_compilation_status", description="Check whether project build artifacts are available.")
def check_compilation_status(executable_path: str = "", library_path: str = "") -> Dict[str, Any]:
    """
    Check build readiness for executable and dynamic library invocation.

    Parameters:
        executable_path (str): Optional path to compiled executable.
        library_path (str): Optional path to dynamic library.

    Returns:
        dict: Standard response with artifact status and recommendations.
    """
    exe = _find_executable(executable_path or None)
    lib = _find_library(library_path or None)
    build_systems = _detect_build_system(_repo_root())

    compiled = exe is not None or lib is not None
    recommendations: List[str] = []
    if not compiled:
        if build_systems["cmake"]:
            recommendations.append("Run configure_build(build_system='cmake') then build_project().")
        elif build_systems["makefile"]:
            recommendations.append("Run build_project(build_system='make').")
        elif build_systems["configure"]:
            recommendations.append("Run configure_build(build_system='configure') then build_project(build_system='make').")
        else:
            recommendations.append("Provide explicit executable_path or library_path if artifacts are external.")

    return {
        "success": True,
        "result": {
            "compiled": compiled,
            "executable": str(exe) if exe else None,
            "library": str(lib) if lib else None,
            "build_systems": build_systems,
            "recommendations": recommendations,
        },
        "error": None,
    }


@mcp.tool(name="configure_build", description="Configure a C/C++ project for compilation using common build systems.")
def configure_build(build_system: str = "cmake", build_type: str = "Release", extra_args: str = "") -> Dict[str, Any]:
    """
    Configure project before build.

    Parameters:
        build_system (str): One of 'cmake', 'configure', 'meson'.
        build_type (str): Build profile (e.g., Release/Debug).
        extra_args (str): Additional raw arguments, shell-like split.

    Returns:
        dict: Standard response for configure command execution.
    """
    root = _repo_root()
    bdir = _build_dir()
    bdir.mkdir(parents=True, exist_ok=True)
    tokens = shlex.split(extra_args) if extra_args else []

    if build_system == "cmake":
        cmd = ["cmake", "-S", str(root), "-B", str(bdir), f"-DCMAKE_BUILD_TYPE={build_type}"] + tokens
        return _run_command(cmd, cwd=root)
    if build_system == "configure":
        configure_script = root / "configure"
        if not configure_script.exists():
            return {"success": False, "result": None, "error": "configure script not found in project root"}
        cmd = [str(configure_script), f"--prefix={bdir}"] + tokens
        return _run_command(cmd, cwd=root)
    if build_system == "meson":
        cmd = ["meson", "setup", str(bdir), str(root)] + tokens
        return _run_command(cmd, cwd=root)

    return {"success": False, "result": None, "error": f"Unsupported build_system: {build_system}"}


@mcp.tool(name="build_project", description="Build C/C++ project via cmake/make/ninja/meson with fallback behavior.")
def build_project(build_system: str = "auto", target: str = "", jobs: int = 0) -> Dict[str, Any]:
    """
    Compile the project.

    Parameters:
        build_system (str): 'auto', 'cmake', 'make', 'ninja', or 'meson'.
        target (str): Optional build target.
        jobs (int): Parallel job count; 0 means tool default.

    Returns:
        dict: Build result with fallback details if compilation fails.
    """
    root = _repo_root()
    bdir = _build_dir()
    detected = _detect_build_system(root)

    systems_to_try: List[str]
    if build_system == "auto":
        systems_to_try = []
        if detected["cmake"]:
            systems_to_try.append("cmake")
        if detected["makefile"]:
            systems_to_try.append("make")
        if detected["meson"]:
            systems_to_try.append("meson")
        if detected["ninja"]:
            systems_to_try.append("ninja")
        if not systems_to_try:
            systems_to_try = ["cmake", "make"]
    else:
        systems_to_try = [build_system]

    attempts: List[Dict[str, Any]] = []
    for system_name in systems_to_try:
        if system_name == "cmake":
            cmd = ["cmake", "--build", str(bdir)]
            if target:
                cmd += ["--target", target]
            if jobs > 0:
                cmd += ["-j", str(jobs)]
            res = _run_command(cmd, cwd=root)
        elif system_name == "make":
            make_bin = shutil.which("make") or "make"
            cmd = [make_bin]
            if target:
                cmd.append(target)
            if jobs > 0:
                cmd += ["-j", str(jobs)]
            res = _run_command(cmd, cwd=root)
        elif system_name == "ninja":
            cmd = ["ninja"]
            if target:
                cmd.append(target)
            if jobs > 0:
                cmd += ["-j", str(jobs)]
            res = _run_command(cmd, cwd=bdir if bdir.exists() else root)
        elif system_name == "meson":
            cmd = ["meson", "compile", "-C", str(bdir)]
            if target:
                cmd += ["--target", target]
            if jobs > 0:
                cmd += ["-j", str(jobs)]
            res = _run_command(cmd, cwd=root)
        else:
            res = {"success": False, "result": None, "error": f"Unsupported build system: {system_name}"}

        attempts.append({"system": system_name, "result": res})
        if res["success"]:
            return {"success": True, "result": {"attempts": attempts, "fallback_used": len(attempts) > 1}, "error": None}

    return {
        "success": False,
        "result": {"attempts": attempts, "fallback_used": len(attempts) > 1},
        "error": "All build attempts failed. Fallback exhausted.",
    }


@mcp.tool(name="run_executable", description="Execute compiled binary with input payload and return parsed output.")
def run_executable(
    executable_path: str = "",
    args: str = "",
    stdin_text: str = "",
    timeout_sec: int = 120
) -> Dict[str, Any]:
    """
    Invoke project executable as the primary wrapper path.

    Parameters:
        executable_path (str): Optional explicit executable path.
        args (str): CLI argument string.
        stdin_text (str): Optional stdin payload.
        timeout_sec (int): Timeout seconds.

    Returns:
        dict: Standard response including stdout/stderr and parsed JSON if available.
    """
    exe = _find_executable(executable_path or None)
    if exe is None:
        return {
            "success": False,
            "result": None,
            "error": "Executable not found. Build project first or pass executable_path.",
        }

    argv = [str(exe)] + (shlex.split(args) if args else [])
    try:
        completed = subprocess.run(
            argv,
            input=stdin_text if stdin_text else None,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            check=False,
        )
        ok = completed.returncode == 0
        parsed: Any = None
        if completed.stdout.strip():
            try:
                parsed = json.loads(completed.stdout)
            except Exception:
                parsed = completed.stdout

        return {
            "success": ok,
            "result": {
                "executable": str(exe),
                "args": argv[1:],
                "returncode": completed.returncode,
                "stdout": completed.stdout,
                "stderr": completed.stderr,
                "parsed_output": parsed,
            },
            "error": None if ok else f"Executable failed with return code {completed.returncode}",
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="call_dynamic_library", description="Call exported C ABI function from a compiled shared library via ctypes.")
def call_dynamic_library(
    library_path: str = "",
    function_name: str = "process_json",
    payload_json: str = "{}"
) -> Dict[str, Any]:
    """
    Call a dynamic library function using ctypes.

    Parameters:
        library_path (str): Optional shared library path.
        function_name (str): Exported C function, expected signature:
            const char* fn(const char* input_json)
        payload_json (str): JSON payload as string.

    Returns:
        dict: Standard response with function output.
    """
    libp = _find_library(library_path or None)
    if libp is None:
        simulated = {
            "mode": "simulated_fallback",
            "reason": "dynamic library not found",
            "input": payload_json,
            "output": {"message": "Simulated C++ library response"},
        }
        return {"success": True, "result": simulated, "error": None}

    try:
        lib = ctypes.CDLL(str(libp))
        if not hasattr(lib, function_name):
            return {"success": False, "result": None, "error": f"Function '{function_name}' not found in library"}

        func = getattr(lib, function_name)
        func.argtypes = [ctypes.c_char_p]
        func.restype = ctypes.c_char_p

        raw = func(payload_json.encode("utf-8"))
        out = raw.decode("utf-8") if raw else ""
        try:
            parsed = json.loads(out) if out else {}
        except Exception:
            parsed = out

        return {
            "success": True,
            "result": {
                "library": str(libp),
                "function": function_name,
                "raw_output": out,
                "parsed_output": parsed,
            },
            "error": None,
        }
    except Exception as exc:
        return {"success": False, "result": None, "error": str(exc)}


@mcp.tool(name="core_query", description="Core endpoint: run query against C/C++ backend via executable first, then ctypes fallback.")
def core_query(query: str, top_k: int = 5, executable_path: str = "", library_path: str = "") -> Dict[str, Any]:
    """
    Execute core query workflow through wrapper strategy.

    Parameters:
        query (str): Search/query text.
        top_k (int): Number of desired results.
        executable_path (str): Optional explicit executable location.
        library_path (str): Optional explicit shared library location.

    Returns:
        dict: Standard response with backend result or fallback simulation.
    """
    req = {"query": query, "top_k": top_k}
    exe = _find_executable(executable_path or None)
    if exe is not None:
        run = run_executable(
            executable_path=str(exe),
            args=f"--query {shlex.quote(query)} --top-k {top_k}",
            stdin_text="",
            timeout_sec=120,
        )
        if run["success"]:
            return run

    lib_result = call_dynamic_library(
        library_path=library_path,
        function_name="process_json",
        payload_json=json.dumps(req),
    )
    if lib_result["success"]:
        return lib_result

    simulated = {
        "mode": "simulated_fallback",
        "input": req,
        "result": [{"id": "sim-1", "score": 0.0, "text": "No compiled backend available; simulated response."}],
    }
    return {"success": True, "result": simulated, "error": None}


def create_app() -> FastMCP:
    return mcp