import subprocess
from pathlib import Path

ROOT_PATH = (Path(__file__).resolve().parent.parent / "workspace").resolve()
ROOT_PATH.mkdir(exist_ok=True)

def run_sandbox(command: list, timeout: int = 30) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=ROOT_PATH,
            capture_output=True,
            text=True,
            timeout=timeout,
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