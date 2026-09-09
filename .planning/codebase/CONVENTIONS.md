# Coding Conventions

**Analysis Date:** 2026-09-09

## Naming Patterns

**Files:**
- Module files: `snake_case.py` (e.g., `agent_core.py`, `sandbox.py`, `verifier.py`)
- Test files: `test_*.py` (configured in `pyproject.toml`)
- Log files: `{session_id}.jsonl` in `audit_logs/`

**Functions & Methods:**
- Functions: `snake_case` (e.g., `run_cli_step`, `generate_plan`, `verify_and_iterate`)
- Internal / private helpers: `_snake_case` with leading underscore (e.g., `_safe_path`, `_group_into_turns`)
- Handlers / callbacks: `on_step` pattern for lifecycle hooks

**Variables:**
- Local variables: `snake_case` (e.g., `task`, `session_id`, `tool_call`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `ROOT_PATH`, `LOG_DIR`, `CODING_SYSTEM_PROMPT`, `TOOLS`, `TOOL_FUNCTIONS`)

**Types & Classes:**
- Classes: `PascalCase` (e.g., `Colors`)
- Type annotations: Standard Python typing (e.g., `str | list`, `dict`, `bool`, `Path`)

## Code Style

**Formatting:**
- Standard Python PEP 8 conventions
- 4-space indentation
- UTF-8 encoding across all file operations (`encoding="utf-8"`)
- Pathlib preferred over raw string path manipulation (`pathlib.Path`)

**Typing:**
- Type hints used across function arguments and return types:
  - `def run_cli_step() -> bool:`
  - `def _safe_path(rel_path: str) -> Path:`
  - `def run_command(command: str | list, timeout: int = 30) -> str:`

## Import Organization

**Order:**
1. Standard library imports (`import os`, `import sys`, `import json`, `from pathlib import Path`, `import subprocess`)
2. Third-party dependencies (`from openai import OpenAI`, `from dotenv import load_dotenv`)
3. Local application modules (`from agent_core import ...`, `import ui`)

*Note: Internal imports in `Agent/` currently use flat module names (e.g., `from tools import ...`) assuming execution from within `Agent/` or with `Agent/` in `sys.path`.*

## Error Handling

**Defensive Validation:**
- Strict boundary checking: `_safe_path()` checks `candidate.is_relative_to(ROOT_PATH)` and raises `ValueError` if paths escape `workspace/`
- Existence verification: `read_file()` and `replace_edit()` raise `FileNotFoundError` with clear error messages
- Exact matching: `replace_edit()` verifies that `old_str` matches exactly once (`count == 1`); if 0 or >1 matches are found, it raises `ValueError` with detailed diagnostic guidance
- Schema retry: `generate_plan()` catches exceptions and retries up to 3 times, passing error feedback to the LLM

**Resilient Tool Dispatch:**
- In `Agent/agent_core.py`, tool argument JSON decoding errors and runtime exceptions are caught and converted into structured error strings (`ERROR: ...`) returned to the model rather than crashing the process. This allows the agent to inspect the failure and correct its action.

**External API Resilience:**
- Rate limiting errors (`openai.RateLimitError`) in `Agent/agent_core.py` trigger automatic retry with exponential/linear backoff up to 5 attempts.

## Logging & Telemetry

**Terminal UX (`Agent/ui.py`):**
- Unified styling via `ui.py` methods:
  - `ui.info(msg)` - Blue informational notices
  - `ui.success(msg)` - Green success indicators
  - `ui.warning(msg)` - Yellow warning notices
  - `ui.error(msg)` - Red error notices
  - `ui.tool_call(tool_name, args)` - Yellow header with formatted parameter preview
  - `ui.tool_result(result_text)` - Green output preview with error highlighting

**Audit Logging (`Agent/audit.py`):**
- Structured append-only JSONL logs written to `audit_logs/{session_id}.jsonl`
- Each record includes:
  - `timestamp`: ISO 8601 UTC timestamp
  - `tool`: Invoked tool name
  - `input`: Parameter dictionary
  - `result`: String result (truncated to 2000 characters)

---

*Conventions analysis: 2026-09-09*\n