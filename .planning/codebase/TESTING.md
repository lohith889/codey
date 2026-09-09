# Testing Patterns

**Analysis Date:** 2026-09-09

## Test Framework

**Runner:**
- `pytest` (v9.1.1, specified as `>=8.0.0` in `pyproject.toml`)
- Configured in `pyproject.toml`:
  ```toml
  [tool.pytest.ini_options]
  pythonpath = ["."]
  testpaths = ["tests"]
  ```

**Run Commands:**
```bash
pytest                        # Run all tests in tests/
uv run pytest                 # Run tests within uv virtual environment
pytest -v                     # Run with verbose output
pytest tests/test_tools.py    # Run a single test module
```

## Test File Organization

**Location:**
- Dedicated `tests/` directory at the project root

**Naming:**
- Test files: `test_*.py`
- Test functions: `test_*()`
- Test classes: `Test*`

**Structure:**
```
codey/
├── Agent/
│   ├── tools.py
│   ├── sandbox.py
│   └── ...
└── tests/
    ├── test_tools.py         # (Recommended) Unit tests for workspace tools
    ├── test_sandbox.py       # (Recommended) Tests for process isolation
    ├── test_planner.py       # (Recommended) Tests for plan validation
    └── test_agent_core.py    # (Recommended) Tests for message pruning and loops
```

## Current Test State & Gaps

**Current Coverage:**
- 0 tests currently implemented (`tests/` directory is empty).
- Running `pytest` exits with code 1 due to `no tests ran`.

**Critical Areas Requiring Tests:**
1. `Agent/tools.py`:
   - Path escaping prevention (`_safe_path` with `../` and absolute paths)
   - `write_file` creation and overwriting
   - `replace_edit` unique replacement, 0-match error, and multi-match error
   - `insert_content` before/after anchor and EOF/top-of-file fallback
   - `list_dir` workspace filtering and git exclusion
2. `Agent/sandbox.py`:
   - Command execution in `workspace/`
   - Timeout handling (`subprocess.TimeoutExpired`)
   - Platform command formatting
3. `Agent/agent_core.py`:
   - `prune_messages` preserving anchors and message-turn groupings
   - Rate limit retry logic
   - Tool function dispatch and error formatting
4. `Agent/planner.py`:
   - Schema validation and retry loop
5. `Agent/audit.py`:
   - JSONL log persistence and markdown rendering

## Mocking Strategy

**LLM Client Mocking:**
- Mock `openai.OpenAI` responses in unit tests to test `run_agent_loop` and `generate_plan` without consuming API credits or requiring network access:
```python
from unittest.mock import MagicMock, patch

@patch("Agent.agent_core.get_client")
def test_agent_loop_tool_call(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    # Configure mock responses for completions.create
```

**Filesystem & Sandbox Mocking:**
- Use pytest's built-in `tmp_path` fixture to point `ROOT_PATH` to temporary directories for isolated filesystem test runs.

## Self-Verification Loop

**Automated Code Verification (`Agent/verifier.py`):**
- Codey includes a built-in verification mechanism (`verify_and_iterate`) that executes user tests inside `workspace/`.
- If tests fail, it diagnoses the output and initiates a self-healing tool loop up to 3 times to fix the code automatically.

---

*Testing analysis: 2026-09-09*\n