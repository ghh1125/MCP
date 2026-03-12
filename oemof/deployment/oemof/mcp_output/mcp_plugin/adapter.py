import os
import sys
import shlex
import subprocess
from typing import Any, Dict, List, Optional

source_path = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "source",
)
sys.path.insert(0, source_path)


class OemofCliAdapter:
    def __init__(
        self,
        python_executable: Optional[str] = None,
        working_dir: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: int = 120,
    ) -> None:
        self.python_executable = python_executable or sys.executable
        self.working_dir = working_dir or os.getcwd()
        self.env = os.environ.copy()
        if env:
            self.env.update(env)
        self.timeout = timeout

    def _run_command(self, cmd: List[str]) -> Dict[str, Any]:
        try:
            completed = subprocess.run(
                cmd,
                cwd=self.working_dir,
                env=self.env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            return {
                "status": "success" if completed.returncode == 0 else "error",
                "returncode": completed.returncode,
                "command": " ".join(shlex.quote(c) for c in cmd),
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip(),
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "error",
                "returncode": -1,
                "command": " ".join(shlex.quote(c) for c in cmd),
                "stdout": (exc.stdout or "").strip() if isinstance(exc.stdout, str) else "",
                "stderr": (exc.stderr or "").strip() if isinstance(exc.stderr, str) else "",
                "error": f"Command timed out after {self.timeout} seconds",
            }
        except FileNotFoundError as exc:
            return {
                "status": "error",
                "returncode": -1,
                "command": " ".join(shlex.quote(c) for c in cmd),
                "stdout": "",
                "stderr": str(exc),
                "error": "Executable not found",
            }
        except Exception as exc:
            return {
                "status": "error",
                "returncode": -1,
                "command": " ".join(shlex.quote(c) for c in cmd),
                "stdout": "",
                "stderr": str(exc),
                "error": "Unexpected execution error",
            }

    def run_oemof_module(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        cmd = [self.python_executable, "-m", "oemof"]
        if args:
            cmd.extend(args)
        return self._run_command(cmd)

    def run_oemof_cli_main(self, args: Optional[List[str]] = None) -> Dict[str, Any]:
        cmd = [self.python_executable, "-m", "oemof.cli"]
        if args:
            cmd.extend(args)
        return self._run_command(cmd)

    def health_check(self) -> Dict[str, Any]:
        checks = {
            "oemof_module": self.run_oemof_module(["--help"]),
            "oemof_cli_main": self.run_oemof_cli_main(["--help"]),
        }
        overall_status = "success" if all(v.get("status") == "success" for v in checks.values()) else "error"
        return {
            "status": overall_status,
            "checks": checks,
        }

    def execute(self, command_name: str, args: Optional[List[str]] = None) -> Dict[str, Any]:
        dispatch = {
            "oemof": self.run_oemof_module,
            "oemof-cli-main": self.run_oemof_cli_main,
        }
        handler = dispatch.get(command_name)
        if handler is None:
            return {
                "status": "error",
                "returncode": -1,
                "stdout": "",
                "stderr": f"Unknown command: {command_name}",
                "error": "Invalid command name",
            }
        return handler(args=args)