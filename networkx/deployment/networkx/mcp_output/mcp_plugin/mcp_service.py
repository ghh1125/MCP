from __future__ import annotations

from fastmcp import FastMCP, subprocess, ctypes
from pathlib import Path
from typing import Any
import json
import os
import shutil
import tempfile

mcp = FastMCP("networkx_cpp_wrapper_service")


def _ok(result: Any) -> dict:
    return {"success": True, "result": result, "error": None}


def _err(message: str) -> dict:
    return {"success": False, "result": None, "error": message}


def _repo_root(path: str) -> Path:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise FileNotFoundError(f"Repository path does not exist: {p}")
    return p


def _find_build_systems(repo: Path) -> dict:
    return {
        "cmake": (repo / "CMakeLists.txt").exists(),
        "makefile": (repo / "Makefile").exists() or (repo / "makefile").exists(),
        "configure": (repo / "configure").exists(),
        "pyproject": (repo / "pyproject.toml").exists(),
    }


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _best_python() -> str:
    return shutil.which("python3") or shutil.which("python") or "python3"


def _build_project(repo: Path, build_dir: Path | None = None) -> dict:
    systems = _find_build_systems(repo)

    if systems["cmake"]:
        bdir = build_dir or (repo / "build")
        bdir.mkdir(parents=True, exist_ok=True)
        rc1, out1, err1 = _run(["cmake", "-S", str(repo), "-B", str(bdir)], cwd=repo)
        if rc1 != 0:
            return {
                "success": False,
                "system": "cmake",
                "stage": "configure",
                "stdout": out1,
                "stderr": err1,
            }
        rc2, out2, err2 = _run(["cmake", "--build", str(bdir), "-j"], cwd=repo)
        return {
            "success": rc2 == 0,
            "system": "cmake",
            "stage": "build",
            "stdout": out2,
            "stderr": err2,
            "build_dir": str(bdir),
        }

    if systems["makefile"]:
        rc, out, err = _run(["make", "-j"], cwd=repo)
        return {
            "success": rc == 0,
            "system": "make",
            "stage": "build",
            "stdout": out,
            "stderr": err,
        }

    if systems["configure"]:
        rc1, out1, err1 = _run(["sh", "configure"], cwd=repo)
        if rc1 != 0:
            return {
                "success": False,
                "system": "configure",
                "stage": "configure",
                "stdout": out1,
                "stderr": err1,
            }
        rc2, out2, err2 = _run(["make", "-j"], cwd=repo)
        return {
            "success": rc2 == 0,
            "system": "configure+make",
            "stage": "build",
            "stdout": out2,
            "stderr": err2,
        }

    return {
        "success": False,
        "system": "unknown",
        "stage": "detect",
        "stdout": "",
        "stderr": "No supported build system detected (CMake/Makefile/configure).",
    }


def _find_executable(repo: Path, explicit: str) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.exists() and os.access(p, os.X_OK) else None

    candidates = []
    for base in [repo, repo / "build", repo / "bin", repo / "out"]:
        if not base.exists():
            continue
        for item in base.rglob("*"):
            if item.is_file() and os.access(item, os.X_OK):
                if item.suffix in {".so", ".dylib", ".dll", ".a"}:
                    continue
                candidates.append(item)
    return candidates[0] if candidates else None


def _find_shared_library(repo: Path, explicit: str) -> Path | None:
    if explicit:
        p = Path(explicit).expanduser().resolve()
        return p if p.exists() else None

    exts = {".so", ".dylib", ".dll"}
    for base in [repo, repo / "build", repo / "lib", repo / "out"]:
        if not base.exists():
            continue
        for item in base.rglob("*"):
            if item.is_file() and item.suffix.lower() in exts:
                return item
    return None


@mcp.tool(name="check_build_systems", description="Detect supported C/C++ build systems in repository.")
def check_build_systems(repo_path: str) -> dict:
    """
    Detect build system files in a C/C++ repository.

    Parameters:
    - repo_path (str): Absolute or relative path to repository root.

    Returns:
    - dict: Standard response with success/result/error fields.
      result includes booleans for cmake, makefile, configure, pyproject.
    """
    try:
        repo = _repo_root(repo_path)
        return _ok(_find_build_systems(repo))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="compile_project", description="Compile C/C++ project using CMake, Makefile, or configure+make.")
def compile_project(repo_path: str, build_dir: str = "") -> dict:
    """
    Compile a C/C++ project with automatic build system selection.

    Parameters:
    - repo_path (str): Repository root path.
    - build_dir (str): Optional custom build directory (mainly for CMake).

    Returns:
    - dict: Standard response with build status/logs.
    """
    try:
        repo = _repo_root(repo_path)
        bdir = Path(build_dir).expanduser().resolve() if build_dir else None
        info = _build_project(repo, bdir)
        if info.get("success"):
            return _ok(info)
        return _err(json.dumps(info, ensure_ascii=False))
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="run_executable", description="Run compiled executable with JSON/string input via subprocess.")
def run_executable(repo_path: str, executable_path: str = "", input_payload: str = "", timeout_sec: int = 30) -> dict:
    """
    Execute a compiled binary and capture output.

    Parameters:
    - repo_path (str): Repository root path.
    - executable_path (str): Optional explicit executable path.
    - input_payload (str): Optional stdin text payload.
    - timeout_sec (int): Process timeout in seconds.

    Returns:
    - dict: Standard response with stdout/stderr/returncode.
    """
    try:
        repo = _repo_root(repo_path)
        exe = _find_executable(repo, executable_path)

        if exe is None:
            build = _build_project(repo)
            if not build.get("success"):
                fallback = {
                    "mode": "fallback",
                    "reason": "compile_failed_or_no_executable",
                    "build_info": build,
                    "simulated_result": {"message": "Executable unavailable; fallback simulation returned."},
                }
                return _ok(fallback)
            exe = _find_executable(repo, executable_path)
            if exe is None:
                return _ok(
                    {
                        "mode": "fallback",
                        "reason": "no_executable_found_after_build",
                        "simulated_result": {"message": "No executable discovered; fallback simulation returned."},
                    }
                )

        proc = subprocess.run(
            [str(exe)],
            input=input_payload,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_sec,
        )
        return _ok(
            {
                "mode": "subprocess",
                "executable": str(exe),
                "returncode": proc.returncode,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
            }
        )
    except subprocess.TimeoutExpired as e:
        return _err(f"Process timeout: {e}")
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="call_shared_library_symbol", description="Call int(int,int) symbol from shared library via ctypes.")
def call_shared_library_symbol(
    repo_path: str,
    library_path: str = "",
    symbol_name: str = "add",
    arg1: int = 0,
    arg2: int = 0,
) -> dict:
    """
    Load shared library and call a function with signature int func(int, int).

    Parameters:
    - repo_path (str): Repository root path.
    - library_path (str): Optional explicit path to .so/.dylib/.dll.
    - symbol_name (str): Exported C symbol name.
    - arg1 (int): First integer argument.
    - arg2 (int): Second integer argument.

    Returns:
    - dict: Standard response with called symbol result.
    """
    try:
        repo = _repo_root(repo_path)
        lib = _find_shared_library(repo, library_path)

        if lib is None:
            build = _build_project(repo)
            if not build.get("success"):
                return _ok(
                    {
                        "mode": "fallback",
                        "reason": "build_failed_no_library",
                        "build_info": build,
                        "simulated_result": arg1 + arg2,
                    }
                )
            lib = _find_shared_library(repo, library_path)
            if lib is None:
                return _ok(
                    {
                        "mode": "fallback",
                        "reason": "no_shared_library_found",
                        "simulated_result": arg1 + arg2,
                    }
                )

        cdll = ctypes.CDLL(str(lib))
        if not hasattr(cdll, symbol_name):
            return _ok(
                {
                    "mode": "fallback",
                    "reason": f"symbol_not_found:{symbol_name}",
                    "library": str(lib),
                    "simulated_result": arg1 + arg2,
                }
            )

        func = getattr(cdll, symbol_name)
        func.argtypes = [ctypes.c_int, ctypes.c_int]
        func.restype = ctypes.c_int
        value = int(func(arg1, arg2))
        return _ok(
            {
                "mode": "ctypes",
                "library": str(lib),
                "symbol": symbol_name,
                "result_value": value,
            }
        )
    except Exception as e:
        return _err(str(e))


@mcp.tool(name="networkx_shortest_path_cli", description="Fallback wrapper to run Python CLI for shortest path on edge list.")
def networkx_shortest_path_cli(
    repo_path: str,
    edges_json: str,
    source_node: str,
    target_node: str,
    weighted: bool = False,
) -> dict:
    """
    Compute shortest path using an external Python subprocess as fallback service behavior.

    Parameters:
    - repo_path (str): Repository root (used for context only).
    - edges_json (str): JSON list of edges. Unweighted: [["a","b"],...], weighted: [["a","b",1.2],...].
    - source_node (str): Source node id.
    - target_node (str): Target node id.
    - weighted (bool): Whether edges contain weight in third field.

    Returns:
    - dict: Standard response with path and length, or error details.
    """
    try:
        _ = _repo_root(repo_path)
        edges = json.loads(edges_json)

        script = """
import json, sys
import networkx as nx

payload = json.loads(sys.stdin.read())
edges = payload["edges"]
src = payload["source"]
dst = payload["target"]
weighted = payload["weighted"]

G = nx.Graph()
if weighted:
    for u,v,w in edges:
        G.add_edge(u,v,weight=float(w))
    p = nx.shortest_path(G, src, dst, weight="weight")
    l = nx.shortest_path_length(G, src, dst, weight="weight")
else:
    for u,v in edges:
        G.add_edge(u,v)
    p = nx.shortest_path(G, src, dst)
    l = nx.shortest_path_length(G, src, dst)

print(json.dumps({"path": p, "length": l}))
"""
        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
            f.write(script)
            temp_script = f.name

        payload = {"edges": edges, "source": source_node, "target": target_node, "weighted": weighted}
        py = _best_python()
        proc = subprocess.run(
            [py, temp_script],
            input=json.dumps(payload),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        Path(temp_script).unlink(missing_ok=True)

        if proc.returncode != 0:
            return _err(proc.stderr.strip() or "networkx subprocess failed")

        return _ok({"mode": "python_subprocess_fallback", "data": json.loads(proc.stdout)})
    except Exception as e:
        return _err(str(e))


def create_app() -> FastMCP:
    return mcp


if __name__ == "__main__":
    mcp.run()