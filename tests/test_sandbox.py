import pytest
import sys
from pathlib import Path
from Agent.sandbox import run_sandbox


@pytest.fixture
def mock_sandbox_workspace(tmp_path, monkeypatch):
    monkeypatch.setattr("Agent.sandbox.ROOT_PATH", tmp_path)
    return tmp_path


def test_run_sandbox_basic_command(mock_sandbox_workspace):
    res = run_sandbox([sys.executable, "-c", "print('sandbox works')"])
    assert res["exit_code"] == 0
    assert "sandbox works" in res["stdout"]
    assert res["stderr"] == ""


def test_run_sandbox_error_exit_code(mock_sandbox_workspace):
    res = run_sandbox([sys.executable, "-c", "import sys; sys.exit(7)"])
    assert res["exit_code"] == 7


def test_run_sandbox_timeout(mock_sandbox_workspace):
    res = run_sandbox([sys.executable, "-c", "import time; time.sleep(5)"], timeout=1)
    assert res["exit_code"] == -1
    assert "timed out after 1s" in res["stderr"]
