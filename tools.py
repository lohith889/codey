import difflib
from pathlib import Path

ROOT_PATH=Path("./workspace").resolve()

def _safe_path(rel_path:str)->Path:
    candidate=(ROOT_PATH/rel_path).resolve()

    if not str(candidate).startswith(str(ROOT_PATH)):
        raise ValueError(f"Path '{rel_path}' escapes the root")

    return candidate

def read_file(rel_path:str)->str:
    print("READING FILES...\n")
    return _safe_path(rel_path).read_text()

def write_file(rel_path:str,content:str)->str:
    print("CREATING FILES...\n")
    path=_safe_path(rel_path)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content)

    return f"Wrote '{content}' to '{rel_path}'"

def edit_file(rel_path:str,old_content:str,new_content:str)->str:
    print("EDITING FILES...\n")
    path=_safe_path(rel_path)
    original=path.read_text()
    count=original.count(old_content)

    if count!=1:
        raise ValueError(f"old str must match exactly 1 time in original file, but found {count} matches")

    updated=original.replace(old_content,new_content,1)
    path.write_text(updated)

    diff="\n".join(difflib.unified_diff(
        original.splitlines(),updated.splitlines(),fromfile=rel_path,tofile=rel_path,lineterm=""
    ))

    return diff

def list_dir(rel_path:str=".")->list:
    print("LISTING FILES...\n")
    path=_safe_path(rel_path)

    return sorted(
        str(f.relative_to(ROOT_PATH)) for f in path.rglob("*") if f.is_file() and ".git" not in f.parts
    )