import pytest
from pathlib import Path
from Agent.tools import (
    _safe_path,
    read_file,
    write_file,
    replace_edit,
    insert_content,
    list_dir,
    run_command,
)


@pytest.fixture
def mock_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr("Agent.tools.ROOT_PATH", tmp_path)
    return tmp_path


def test_safe_path_valid(mock_workspace):
    path = _safe_path("subdir/file.txt")
    assert path == mock_workspace / "subdir" / "file.txt"
    assert path.is_relative_to(mock_workspace)


def test_safe_path_traversal_attack(mock_workspace):
    with pytest.raises(ValueError, match="escapes workspace root"):
        _safe_path("../../outside.txt")


def test_write_and_read_file(mock_workspace):
    rel_path = "nested/dir/hello.py"
    content = "print('Hello, world!')"
    msg = write_file(rel_path, content)
    assert "Successfully wrote 1 lines" in msg

    read_back = read_file(rel_path)
    assert read_back == content


def test_read_file_not_found(mock_workspace):
    with pytest.raises(FileNotFoundError):
        read_file("non_existent.txt")


def test_replace_edit_success(mock_workspace):
    rel_path = "app.py"
    write_file(rel_path, "def main():\n    print('old')\n")

    diff = replace_edit(rel_path, "print('old')", "print('new')")
    assert "-    print('old')" in diff
    assert "+    print('new')" in diff

    updated = read_file(rel_path)
    assert "print('new')" in updated
    assert "print('old')" not in updated


def test_replace_edit_not_found(mock_workspace):
    rel_path = "app.py"
    write_file(rel_path, "x = 10")

    with pytest.raises(ValueError, match="old_str not found"):
        replace_edit(rel_path, "y = 20", "y = 30")


def test_replace_edit_multiple_matches(mock_workspace):
    rel_path = "app.py"
    write_file(rel_path, "foo = 1\nfoo = 1\n")

    with pytest.raises(ValueError, match="matched 2 times"):
        replace_edit(rel_path, "foo = 1", "foo = 2")


def test_insert_content_after_target(mock_workspace):
    rel_path = "notes.txt"
    write_file(rel_path, "line1\nline2\n")

    insert_content(rel_path, "inserted\n", target="line1\n", position="after")
    content = read_file(rel_path)
    assert content == "line1\ninserted\nline2\n"


def test_insert_content_before_target(mock_workspace):
    rel_path = "notes.txt"
    write_file(rel_path, "line1\nline2\n")

    insert_content(rel_path, "inserted\n", target="line2", position="before")
    content = read_file(rel_path)
    assert content == "line1\ninserted\nline2\n"


def test_insert_content_append_eof(mock_workspace):
    rel_path = "notes.txt"
    write_file(rel_path, "line1\n")

    insert_content(rel_path, "line2", target=None, position="after")
    content = read_file(rel_path)
    assert content == "line1\nline2"


def test_insert_content_prepend_top(mock_workspace):
    rel_path = "notes.txt"
    write_file(rel_path, "line2\n")

    insert_content(rel_path, "line1", target=None, position="before")
    content = read_file(rel_path)
    assert content == "line1\nline2\n"


def test_insert_content_invalid_position(mock_workspace):
    rel_path = "notes.txt"
    write_file(rel_path, "line1\n")

    with pytest.raises(ValueError, match="position must be either"):
        insert_content(rel_path, "data", position="middle")


def test_list_dir(mock_workspace):
    write_file("src/main.py", "pass")
    write_file("src/utils.py", "pass")
    write_file("docs/readme.md", "# Docs")

    files = list_dir(".")
    assert sorted(files) == ["docs\\readme.md", "src\\main.py", "src\\utils.py"] or sorted(files) == ["docs/readme.md", "src/main.py", "src/utils.py"]
