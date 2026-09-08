import platform
import subprocess
from pathlib import Path

ROOT_PATH = (Path(__file__).resolve().parent.parent / "workspace").resolve()
ROOT_PATH.mkdir(exist_ok=True)

def run_sandbox(command: list | str, timeout: int = 30) -> dict:
    is_windows = platform.system() == "Windows"

    if isinstance(command, list):
        cmd = subprocess.list2cmdline(command) if is_windows else command
    else:
        cmd = command

    try:
        result = subprocess.run(
            cmd,
            cwd=ROOT_PATH,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=is_windows,
        )

        return {
            "stdout": result.stdout[-4000:],
            "stderr": result.stderr[-4000:],
            "exit_code": result.returncode,
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "exit_code": -1,
        }
    except Exception as exc:
        return {
            "stdout": "",
            "stderr": f"Sandbox execution error: {exc}",
            "exit_code": -1,
        }