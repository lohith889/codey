<!-- GSD:project-start source:PROJECT.md -->

## Project

**Codey**

Codey is an autonomous AI pair-programming assistant built in Python that translates high-level developer tasks into structured execution plans and executes them using sandboxed filesystem and terminal tools. Designed for terminal-centric workflows, Codey enables developers to safely delegate multi-step coding, refactoring, and test-driven bug fixing tasks with human-in-the-loop supervision.

**Core Value:** Reliable, user-supervised autonomous code editing and verification that operates safely inside a sandboxed workspace without corrupting user repositories.

### Constraints

- **Tech stack**: Python >=3.11, `openai>=1.0.0`, `python-dotenv>=1.0.0`, `pytest>=8.0.0`
- **Security**: Strict filesystem boundary enforcement keeping all agent edits within `workspace/`
- **Platform**: Cross-platform compatibility for Windows (PowerShell/cmd) and POSIX systems

<!-- GSD:project-end -->

<!-- GSD:stack-start source:codebase/STACK.md -->

## Technology Stack

## Languages

- Python 3.11+ (verified runtime: Python 3.11.9) - All application code including planning, execution engine, CLI, sandboxing, and audit logging in `Agent/`
- None (pure Python project)

## Runtime

- Python 3.11.9 (CPython)
- Cross-platform support for Windows and POSIX systems. Specifically includes Windows console ANSI escape sequence initialization in `Agent/ui.py` and `subprocess.list2cmdline` command serialization in `Agent/sandbox.py`
- `uv` (v0.12.5)
- Lockfile: `uv.lock` present and tracked in version control

## Frameworks

- None (custom lightweight autonomous agent engine built on Python standard library and OpenAI SDK)
- `pytest` (v9.1.1, specified as `>=8.0.0` in `pyproject.toml`) configured via `[tool.pytest.ini_options]` in `pyproject.toml`
- `uv_build` (v0.12.5, `>=0.12.5,<0.13.0`) as build-backend in `pyproject.toml`
- `python-dotenv` (v1.0.0+) for environment variable loading from `.env`

## Key Dependencies

- `openai>=1.0.0` - Powers model completions, structured JSON schema response enforcement in `Agent/planner.py`, and ReAct tool-calling loops in `Agent/agent_core.py`
- `python-dotenv>=1.0.0` - Automatically loads local environment configuration and API credentials in `Agent/agent_core.py` and `Agent/planner.py`
- `pytest>=8.0.0` - Test discovery and execution engine
- `pathlib.Path` - Path manipulation and strict workspace boundary validation in `Agent/tools.py` and `Agent/sandbox.py`
- `subprocess` - Isolated child process execution inside `workspace/` in `Agent/sandbox.py`
- `difflib` - Unified diff generation for file edits and insertions in `Agent/tools.py`
- `json` - Tool arguments parsing and structured plan serialization
- `shlex` - Safe POSIX/Windows command string parsing in `Agent/cli.py`, `Agent/tools.py`, and `Agent/verifier.py`
- `uuid` & `datetime` - Unique session ID generation and ISO UTC audit logging in `Agent/audit.py`

## Configuration

- Configured via `.env` file (loaded via `dotenv.load_dotenv()`)
- Key environment variables:
- `pyproject.toml` - Project packaging metadata, dependencies, entry point script `codey = "Agent.cli:main"`, and pytest testpaths

## Platform Requirements

- Windows / macOS / Linux with Python >=3.11
- `uv` recommended for environment isolation and dependency resolution
- Valid OpenAI/Groq compatible API key in `.env`
- CLI application executable via `python Agent/cli.py` or entry point script `codey`
- Runtime workspace dynamically created at `workspace/` relative to project root

<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

## Naming Patterns

- Module files: `snake_case.py` (e.g., `agent_core.py`, `sandbox.py`, `verifier.py`)
- Test files: `test_*.py` (configured in `pyproject.toml`)
- Log files: `{session_id}.jsonl` in `audit_logs/`
- Functions: `snake_case` (e.g., `run_cli_step`, `generate_plan`, `verify_and_iterate`)
- Internal / private helpers: `_snake_case` with leading underscore (e.g., `_safe_path`, `_group_into_turns`)
- Handlers / callbacks: `on_step` pattern for lifecycle hooks
- Local variables: `snake_case` (e.g., `task`, `session_id`, `tool_call`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `ROOT_PATH`, `LOG_DIR`, `CODING_SYSTEM_PROMPT`, `TOOLS`, `TOOL_FUNCTIONS`)
- Classes: `PascalCase` (e.g., `Colors`)
- Type annotations: Standard Python typing (e.g., `str | list`, `dict`, `bool`, `Path`)

## Code Style

- Standard Python PEP 8 conventions
- 4-space indentation
- UTF-8 encoding across all file operations (`encoding="utf-8"`)
- Pathlib preferred over raw string path manipulation (`pathlib.Path`)
- Type hints used across function arguments and return types:

## Import Organization

## Error Handling

- Strict boundary checking: `_safe_path()` checks `candidate.is_relative_to(ROOT_PATH)` and raises `ValueError` if paths escape `workspace/`
- Existence verification: `read_file()` and `replace_edit()` raise `FileNotFoundError` with clear error messages
- Exact matching: `replace_edit()` verifies that `old_str` matches exactly once (`count == 1`); if 0 or >1 matches are found, it raises `ValueError` with detailed diagnostic guidance
- Schema retry: `generate_plan()` catches exceptions and retries up to 3 times, passing error feedback to the LLM
- In `Agent/agent_core.py`, tool argument JSON decoding errors and runtime exceptions are caught and converted into structured error strings (`ERROR: ...`) returned to the model rather than crashing the process. This allows the agent to inspect the failure and correct its action.
- Rate limiting errors (`openai.RateLimitError`) in `Agent/agent_core.py` trigger automatic retry with exponential/linear backoff up to 5 attempts.

## Logging & Telemetry

- Unified styling via `ui.py` methods:
- Structured append-only JSONL logs written to `audit_logs/{session_id}.jsonl`
- Each record includes:

<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

## Pattern Overview

- Two-stage architecture: Structured plan synthesis followed by ReAct tool execution
- Isolated filesystem workspace: All generated and edited files are constrained within `workspace/`
- Human-in-the-loop gate: Plan approval required before execution proceeds
- Closed-loop verification: Automated test execution and multi-turn error self-healing via `Agent/verifier.py`
- Stateful session audit: Every tool invocation and result logged to JSONL for auditability

## Layers

- Purpose: CLI interface, ANSI color terminal rendering, interactive REPL loop, and plan approval prompts
- Contains: `run_cli_step()`, `main()`, `ui.Colors`, `ui.banner()`, `ui.print_plan()`, `ui.tool_call()`
- Depends on: Planning layer, Agent Core, Verifier, Audit
- Used by: End user invoking the CLI
- Purpose: Converts user tasks into a decomposed, structured execution plan conforming to a strict JSON schema
- Contains: `generate_plan()`, `steps_schema`, `PLANNER_SYSTEM_PROMPT`
- Depends on: `openai.OpenAI` client (via `Agent/agent_core.py:get_client`), `Agent/ui.py`
- Used by: `Agent/cli.py`
- Purpose: Executes the ReAct tool loop, manages LLM communication, handles rate limits, parses tool calls, prunes context history, and dispatches tool execution
- Contains: `run_agent_loop()`, `get_client()`, `prune_messages()`, `_group_into_turns()`, `CODING_SYSTEM_PROMPT`, `TOOLS`, `TOOL_FUNCTIONS`
- Depends on: `Agent/tools.py`, `Agent/ui.py`, `openai`
- Used by: `Agent/cli.py`, `Agent/verifier.py`
- Purpose: Provides safe file operations (read, write, replace, insert, list) and command execution
- Contains: `_safe_path()`, `read_file()`, `write_file()`, `replace_edit()`, `insert_content()`, `append_after()`, `append_before()`, `list_dir()`, `run_command()`
- Depends on: `Agent/sandbox.py`, `pathlib.Path`, `difflib`
- Used by: `Agent/agent_core.py`
- Purpose: Safely runs subprocess commands constrained inside the `workspace/` working directory with timeouts and cross-platform shell support
- Contains: `run_sandbox()`
- Depends on: `subprocess`, `platform`, `pathlib.Path`
- Used by: `Agent/tools.py`, `Agent/verifier.py`
- Purpose: Automated test verification and iterative defect repair
- Contains: `verify_and_iterate()`
- Depends on: `Agent/sandbox.py`, `Agent/agent_core.py`
- Used by: `Agent/cli.py` (`/test` command)
- Purpose: Persists immutable execution logs for every tool call and provides markdown audit rendering
- Contains: `log_step()`, `render_audit_markdown()`
- Depends on: `json`, `datetime`, `pathlib.Path`
- Used by: `Agent/cli.py`

## Data Flow

- Conversation State: In-memory list of messages pruned via `prune_messages()`.
- File State: Written to disk inside `workspace/`.
- Audit State: Appended to `audit_logs/{session_id}.jsonl`.

## Key Abstractions

- Location: `Agent/tools.py`
- Purpose: Guarantees that no file read or write operation escapes `D:\lohith\codey\workspace`.
- Pattern: Security barrier / Path normalization check.
- Location: `Agent/agent_core.py`
- Purpose: Preserves the first two anchor messages (system prompt + user task) while trimming older conversation turns to prevent context window overflow.
- Pattern: Sliding-window turn aggregation.
- Location: `Agent/planner.py`
- Purpose: Enforces strict JSON Schema for step ID, description, and files touched before code execution begins.
- Pattern: Schema validation gate.

## Entry Points

- Location: `Agent/cli.py:main`
- Invocation: `python Agent/cli.py` or console script `codey` (configured in `pyproject.toml`)
- Responsibilities: Displays ASCII banner, reads user input, handles `/test` and `exit`, runs plan-approve-execute loop.

## Error Handling

- Handled in `Agent/agent_core.py` catching `openai.RateLimitError` with up to 5 retries and exponential/linear backoff.
- Exceptions during tool execution (e.g. `ValueError`, `FileNotFoundError`) are caught in `Agent/agent_core.py` and returned as string error messages (`ERROR: ...`) to the LLM, enabling autonomous self-correction.
- `replace_edit` enforces exact match count (`count == 1`). If `old_str` matches 0 or >1 times, it raises a descriptive `ValueError` with suggestions.
- `insert_content` enforces target anchor uniqueness before inserting content.

## Cross-Cutting Concerns

- Encapsulated in `Agent/ui.py` with automatic Windows console ANSI escape enablement (`os.system("")` on `nt`).
- Every tool action across any session is logged to `audit_logs/` for tracking and diagnostics.

<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.agents/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `/gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `/gsd-debug` for investigation and bug fixing
- `/gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `/gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
