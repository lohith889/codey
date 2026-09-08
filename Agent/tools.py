import difflib
from pathlib import Path
from typing import List, Union

ROOT_PATH = Path("./workspace").resolve()


def _safe_path(rel_path: str) -> Path:
    """Validate that a path stays within the workspace root."""
    candidate = (ROOT_PATH / rel_path).resolve()

    if not str(candidate).startswith(str(ROOT_PATH)):
        raise ValueError(f"Path '{rel_path}' escapes the root directory")

    return candidate


def read_file(rel_path: str) -> str:
    """Read the contents of a file."""
    print(f"📖 READING: {rel_path}")
    path = _safe_path(rel_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {rel_path}")
    
    return path.read_text(encoding='utf-8')


def write_file(rel_path: str, content: str) -> str:
    """Create or overwrite a file with the given content."""
    print(f"📝 WRITING: {rel_path}")
    path = _safe_path(rel_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

    line_count = len(content.splitlines())
    char_count = len(content)
    return f"✅ Wrote {line_count} lines ({char_count} chars) to '{rel_path}'"


def edit_file(rel_path: str, old_str: str, new_str: str) -> str:
    """Replace one exact string occurrence in a file."""
    print(f"✏️  EDITING: {rel_path}")
    path = _safe_path(rel_path)
    original = path.read_text(encoding='utf-8')
    count = original.count(old_str)

    if count == 0:
        raise ValueError(f"'old_str' not found in file '{rel_path}'")
    if count > 1:
        raise ValueError(f"'old_str' appears {count} times in file. Must be unique.")

    updated = original.replace(old_str, new_str, 1)
    path.write_text(updated, encoding='utf-8')

    diff = "\n".join(difflib.unified_diff(
        original.splitlines(), updated.splitlines(),
        fromfile=rel_path, tofile=rel_path, lineterm=""
    ))

    return f"✅ Edited '{rel_path}'\n\n{diff}"


def list_dir(rel_path: str = ".") -> List[str]:
    """List all files in a directory recursively."""
    print(f"📁 LISTING: {rel_path}")
    path = _safe_path(rel_path)

    if not path.exists():
        raise FileNotFoundError(f"Directory not found: {rel_path}")

    files = sorted(
        str(f.relative_to(ROOT_PATH)) 
        for f in path.rglob("*") 
        if f.is_file() and ".git" not in f.parts
    )
    
    if not files:
        return ["(empty directory)"]
    
    return files
