import subprocess
from pathlib import Path
from typing import List, Dict

ROOT_PATH = Path('./workspace').resolve()


def run_sandbox(command: List[str], timeout: int = 30) -> Dict:
    """Execute a command in a sandboxed environment with proper error handling."""
    try:
        result = subprocess.run(
            command,
            cwd=ROOT_PATH,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )

        return {
            "stdout": result.stdout[-4000:] if result.stdout else "",
            "stderr": result.stderr[-4000:] if result.stderr else "",
            "exit_code": result.returncode,
            "command": " ".join(command),
        }

    except subprocess.TimeoutExpired:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout}s",
            "exit_code": -1,
            "command": " ".join(command),
        }
    except FileNotFoundError as e:
        return {
            "stdout": "",
            "stderr": f"Command not found: {e.filename}",
            "exit_code": -2,
            "command": " ".join(command),
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "exit_code": -3,
            "command": " ".join(command),
        }