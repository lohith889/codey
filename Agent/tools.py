import difflib
from pathlib import Path
import shlex
from Agent.sandbox import run_sandbox

ROOT_PATH = (Path(__file__).resolve().parent.parent / "workspace").resolve()
ROOT_PATH.mkdir(exist_ok=True)


def _safe_path(rel_path: str) -> Path:
    candidate = (ROOT_PATH / rel_path).resolve()
    if not candidate.is_relative_to(ROOT_PATH):
        raise ValueError(f"Path '{rel_path}' escapes workspace root")
    return candidate


def read_file(rel_path: str) -> str:
    print("READING FILES...\n")
    path = _safe_path(rel_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: '{rel_path}'")
    return path.read_text(encoding="utf-8")


def write_file(rel_path: str, content: str) -> str:
    print("CREATING FILES...\n")
    path = _safe_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    line_count = len(content.splitlines())
    return f"Successfully wrote {line_count} lines ({len(content)} bytes) to '{rel_path}'"


def edit_file(rel_path: str, old_content: str, new_content: str) -> str:
    print("EDITING FILES...\n")
    path = _safe_path(rel_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: '{rel_path}'")
    original = path.read_text(encoding="utf-8")
    count = original.count(old_content)

    if count != 1:
        raise ValueError(
            f"old_str must match exactly 1 time in '{rel_path}', but found {count} matches"
        )

    updated = original.replace(old_content, new_content, 1)
    path.write_text(updated, encoding="utf-8")

    diff = "\n".join(
        difflib.unified_diff(
            original.splitlines(),
            updated.splitlines(),
            fromfile=rel_path,
            tofile=rel_path,
            lineterm="",
        )
    )

    return diff or "(No visual differences)"


def list_dir(rel_path: str = ".") -> list:
    print("LISTING FILES...\n")
    path = _safe_path(rel_path)
    if not path.exists():
        return []
    if path.is_file():
        return [str(path.relative_to(ROOT_PATH))]

    return sorted(
        str(f.relative_to(ROOT_PATH))
        for f in path.rglob("*")
        if f.is_file() and ".git" not in f.parts
    )


def run_command(command: str | list, timeout: int = 30) -> str:
    print(f"RUNNING COMMAND: {command}\n")
    if isinstance(command, str):
        command = shlex.split(command)
    res = run_sandbox(command, timeout=timeout)
    parts = []
    if res.get("stdout"):
        parts.append(f"STDOUT:\n{res['stdout']}")
    if res.get("stderr"):
        parts.append(f"STDERR:\n{res['stderr']}")
    parts.append(f"Exit code: {res.get('exit_code', -1)}")
    return "\n".join(parts)