import difflib
from pathlib import Path
import shlex
try:
    from Agent.sandbox import run_sandbox
except ImportError:
    from sandbox import run_sandbox

ROOT_PATH = (Path(__file__).resolve().parent.parent / "workspace").resolve()
ROOT_PATH.mkdir(exist_ok=True)


def _safe_path(rel_path: str) -> Path:
    candidate = (ROOT_PATH / rel_path).resolve()
    if not candidate.is_relative_to(ROOT_PATH):
        raise ValueError(f"Path '{rel_path}' escapes workspace root")
    return candidate


def read_file(rel_path: str) -> str:
    path = _safe_path(rel_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: '{rel_path}'")
    return path.read_text(encoding="utf-8")


def write_file(rel_path: str, content: str) -> str:
    path = _safe_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    line_count = len(content.splitlines())
    return f"Successfully wrote {line_count} lines ({len(content)} bytes) to '{rel_path}'"


def replace_edit(rel_path: str, old_str: str, new_str: str) -> str:
    path = _safe_path(rel_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: '{rel_path}'")

    original = path.read_text(encoding="utf-8")
    count = original.count(old_str)

    if count == 0:
        raise ValueError(
            f"old_str not found in '{rel_path}'. Please check whitespace and indentation:\n{old_str!r}"
        )
    if count > 1:
        raise ValueError(
            f"old_str matched {count} times in '{rel_path}'. Include more surrounding context to ensure a unique match."
        )

    updated = original.replace(old_str, new_str, 1)
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


def insert_content(
    rel_path: str,
    content: str,
    target: str | None = None,
    position: str = "after",
) -> str:
    """
    Append before or append after a target string in a file.
    - position='after': inserts content immediately AFTER target (or at EOF if target is omitted).
    - position='before': inserts content immediately BEFORE target (or at top of file if target is omitted).
    """
    pos = position.lower().strip()
    if pos not in ("before", "after"):
        raise ValueError("position must be either 'before' or 'after'")

    path = _safe_path(rel_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: '{rel_path}'")

    original = path.read_text(encoding="utf-8")

    if target:
        count = original.count(target)
        if count == 0:
            raise ValueError(
                f"target anchor not found in '{rel_path}'. Please check whitespace and indentation:\n{target!r}"
            )
        if count > 1:
            raise ValueError(
                f"target anchor matched {count} times in '{rel_path}'. Include more surrounding context to make it unique."
            )

        if pos == "after":
            idx = original.index(target) + len(target)
        else:
            idx = original.index(target)

        updated = original[:idx] + content + original[idx:]
    else:
        if pos == "after":
            separator = "\n" if original and not original.endswith("\n") and not content.startswith("\n") else ""
            updated = original + separator + content
        else:
            separator = "\n" if not content.endswith("\n") and not original.startswith("\n") else ""
            updated = content + separator + original

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


def append_after(rel_path: str, target: str, content: str) -> str:
    return insert_content(rel_path, content, target=target, position="after")


def append_before(rel_path: str, target: str, content: str) -> str:
    return insert_content(rel_path, content, target=target, position="before")


# Backwards compatibility alias
edit_file = replace_edit


def list_dir(rel_path: str = ".") -> list:
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