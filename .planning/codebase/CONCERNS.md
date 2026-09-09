# Codebase Concerns

**Analysis Date:** 2026-09-09

## Tech Debt

**1. Unqualified Internal Module Imports in `Agent/`:**
- Issue: Files inside `Agent/` use unqualified top-level imports (e.g., `from agent_core import ...` in `cli.py`, `from tools import ...` in `agent_core.py`, `from sandbox import run_sandbox` in `tools.py`).
- Why: Initially developed with all scripts residing in the project root directory before being reorganized into `Agent/` (commit `bfbec35`).
- Impact: Running the console script `codey` (defined in `pyproject.toml` as `codey = "Agent.cli:main"`) or importing `Agent.cli` from outside the directory fails with `ModuleNotFoundError: No module named 'agent_core'`. The CLI currently only runs when `Agent/` is in `sys.path` (e.g. running `python Agent/cli.py` directly).
- Fix approach: Update internal imports to package-relative imports (e.g. `from .agent_core import ...`) or fully-qualified imports (`from Agent.agent_core import ...`), and ensure `Agent/__init__.py` exists.

**2. Missing `Agent/__init__.py`:**
- Issue: `Agent/` directory lacks an `__init__.py` file.
- Why: Python 3.3+ namespace packages allow imports without `__init__.py`, but explicit package declaration is best practice for tools and linters.
- Impact: Inconsistent package resolution across tooling and packaging systems.
- Fix approach: Add `Agent/__init__.py`.

**3. Hardcoded Groq/OpenAI Model Coupling:**
- Issue: Default model `openai/gpt-oss-20b` and base URL `https://api.groq.com/openai/v1` are specific to Groq.
- Why: Optimized for Groq's fast inference speeds.
- Impact: If a standard OpenAI API key is supplied without changing `MODEL_NAME` or `GROQ_BASE_URL`, requests fail because `openai/gpt-oss-20b` does not exist on standard OpenAI.
- Fix approach: Support explicit provider detection or distinct environment configuration profiles (e.g., `PROVIDER=groq|openai`).

## Known Bugs & Edge Cases

**1. Test Suite Exit Code Failure:**
- Symptoms: Running `pytest` immediately returns exit code 1.
- Root cause: `tests/` directory has zero test files; pytest exits with code 1 when no tests are collected.
- Workaround: Pass `-o empty_parameter=...` or add placeholder tests.
- Fix approach: Implement initial test coverage in `tests/`.

**2. `/test` Command Input UX:**
- Symptoms: When typing `/test` in the CLI prompt, it asks `Test command to verify (blank to skip):` without listing available test runners or project defaults.
- Impact: Users must manually remember and type the full command (e.g., `pytest`).
- Fix approach: Provide a sensible default (e.g., detect `pytest` or `python -m unittest`).

## Security Considerations

**1. Arbitrary Shell Execution via `run_sandbox`:**
- Risk: `Agent/sandbox.py` executes commands with `shell=True` on Windows using `cmd` or PowerShell. Although `cwd` is set to `workspace/`, commands executed by the agent inherit the full permissions of the running user. A rogue command (or prompt injection) could execute commands outside `workspace/` (e.g. `cd .. && dir`).
- Current mitigation: `Agent/tools.py:_safe_path` prevents filesystem tool escapes, but shell commands in `run_command` can bypass filesystem restrictions.
- Recommendations: Implement command allowlisting or sanitize shell arguments.

**2. API Key Management:**
- Risk: API keys stored in plaintext `.env`.
- Current mitigation: `.env` is listed in `.gitignore`.
- Recommendations: Ensure documentation clearly instructs users not to commit `.env`.

## Performance Bottlenecks

**1. Sequential Tool Execution:**
- Problem: `Agent/agent_core.py` executes multiple tool calls sequentially in a single turn.
- Impact: For tasks requiring multiple file reads or writes, total latency is bounded by sequential disk I/O and process execution.
- Improvement path: Parallelize independent read operations where applicable.

**2. History Pruning Truncation:**
- Problem: `prune_messages` aggressively enforces `max_messages=20`.
- Impact: For complex multi-turn tasks requiring extensive tool iterations, earlier file context and diagnostic messages are dropped, potentially causing the model to repeat mistakes.
- Improvement path: Implement token-based dynamic budget management or summarized memory.

## Fragile Areas

**1. `replace_edit` Exact Match Requirement:**
- Why fragile: Requires an exact character-for-character match of `old_str`. Any discrepancy in whitespace, indentation (tabs vs spaces), or line endings causes the edit to fail.
- Common failures: LLM generates normalized indentation or omits surrounding lines, leading to `ValueError: old_str not found`.
- Safe modification: Use `insert_content` or `write_file` for complete rewrites when exact replacement fails.

**2. Structured Outputs JSON Schema Support:**
- Why fragile: `Agent/planner.py` uses `response_format={"type": "json_schema", ...}` with `strict: True`.
- Impact: Only certain OpenAI and Groq models support strict JSON schema response formats. Using models without structured output capabilities causes API 400 errors.

## Missing Critical Features

- Automated unit and integration test suite in `tests/`
- Interactive plan editing (currently only binary approve/reject `[y/n]`)
- Multi-file diff review before applying agent changes
- Token usage tracking and cost metrics

---

*Concerns analysis: 2026-09-09*\n