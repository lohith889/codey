# Architecture

**Analysis Date:** 2026-09-09

## Pattern Overview

**Overall:** Plan-and-Execute Autonomous Coding Agent with Sandboxed Tool Execution and Self-Correction Loop.

**Key Characteristics:**
- Two-stage architecture: Structured plan synthesis followed by ReAct tool execution
- Isolated filesystem workspace: All generated and edited files are constrained within `workspace/`
- Human-in-the-loop gate: Plan approval required before execution proceeds
- Closed-loop verification: Automated test execution and multi-turn error self-healing via `Agent/verifier.py`
- Stateful session audit: Every tool invocation and result logged to JSONL for auditability

## Layers

**Presentation Layer (`Agent/cli.py`, `Agent/ui.py`):**
- Purpose: CLI interface, ANSI color terminal rendering, interactive REPL loop, and plan approval prompts
- Contains: `run_cli_step()`, `main()`, `ui.Colors`, `ui.banner()`, `ui.print_plan()`, `ui.tool_call()`
- Depends on: Planning layer, Agent Core, Verifier, Audit
- Used by: End user invoking the CLI

**Planning Layer (`Agent/planner.py`):**
- Purpose: Converts user tasks into a decomposed, structured execution plan conforming to a strict JSON schema
- Contains: `generate_plan()`, `steps_schema`, `PLANNER_SYSTEM_PROMPT`
- Depends on: `openai.OpenAI` client (via `Agent/agent_core.py:get_client`), `Agent/ui.py`
- Used by: `Agent/cli.py`

**Agent Orchestration Layer (`Agent/agent_core.py`):**
- Purpose: Executes the ReAct tool loop, manages LLM communication, handles rate limits, parses tool calls, prunes context history, and dispatches tool execution
- Contains: `run_agent_loop()`, `get_client()`, `prune_messages()`, `_group_into_turns()`, `CODING_SYSTEM_PROMPT`, `TOOLS`, `TOOL_FUNCTIONS`
- Depends on: `Agent/tools.py`, `Agent/ui.py`, `openai`
- Used by: `Agent/cli.py`, `Agent/verifier.py`

**Tool Execution Layer (`Agent/tools.py`):**
- Purpose: Provides safe file operations (read, write, replace, insert, list) and command execution
- Contains: `_safe_path()`, `read_file()`, `write_file()`, `replace_edit()`, `insert_content()`, `append_after()`, `append_before()`, `list_dir()`, `run_command()`
- Depends on: `Agent/sandbox.py`, `pathlib.Path`, `difflib`
- Used by: `Agent/agent_core.py`

**Sandbox & Execution Layer (`Agent/sandbox.py`):**
- Purpose: Safely runs subprocess commands constrained inside the `workspace/` working directory with timeouts and cross-platform shell support
- Contains: `run_sandbox()`
- Depends on: `subprocess`, `platform`, `pathlib.Path`
- Used by: `Agent/tools.py`, `Agent/verifier.py`

**Verification & Iteration Layer (`Agent/verifier.py`):**
- Purpose: Automated test verification and iterative defect repair
- Contains: `verify_and_iterate()`
- Depends on: `Agent/sandbox.py`, `Agent/agent_core.py`
- Used by: `Agent/cli.py` (`/test` command)

**Telemetry & Audit Layer (`Agent/audit.py`):**
- Purpose: Persists immutable execution logs for every tool call and provides markdown audit rendering
- Contains: `log_step()`, `render_audit_markdown()`
- Depends on: `json`, `datetime`, `pathlib.Path`
- Used by: `Agent/cli.py`

## Data Flow

**1. Normal Interactive Flow:**
1. User enters task description at the `Task >` CLI prompt (`Agent/cli.py`).
2. `generate_plan()` sends task to LLM with `steps_schema` to produce structured step list.
3. CLI prints proposed plan and prompts user for approval (`[y/n]`).
4. Upon approval, `run_agent_loop()` initiates with system prompt + plan context.
5. In each iteration:
   - LLM responds with one or more function calls (`read_file`, `write_file`, `replace_edit`, `insert_content`, `list_dir`, `run_command`).
   - Tool arguments are validated and executed against `workspace/`.
   - Tool execution is logged to `audit_logs/{session_id}.jsonl` via `on_step` callback.
   - Tool results are returned as `tool` messages to the LLM.
   - Message history is pruned to `max_messages=20` keeping initial anchors intact.
6. When no further tool calls are emitted, the loop terminates and outputs the final response.

**2. Automated Verification Flow (`/test` command):**
1. User supplies a test command string (e.g., `pytest`).
2. `verify_and_iterate()` executes command via `run_sandbox()` inside `workspace/`.
3. If exit code is 0: returns pass status immediately.
4. If exit code is non-zero: formats diagnostic prompt containing exit code, stdout, and stderr.
5. Invokes `run_agent_loop()` with fix task to diagnose and modify files in `workspace/`.
6. Repeats verification up to `max_retries` (3 attempts).

**State Management:**
- Conversation State: In-memory list of messages pruned via `prune_messages()`.
- File State: Written to disk inside `workspace/`.
- Audit State: Appended to `audit_logs/{session_id}.jsonl`.

## Key Abstractions

**Workspace Boundary Enforcement (`_safe_path`):**
- Location: `Agent/tools.py`
- Purpose: Guarantees that no file read or write operation escapes `D:\lohith\codey\workspace`.
- Pattern: Security barrier / Path normalization check.

**Conversation Anchors & Turn Pruning (`prune_messages`):**
- Location: `Agent/agent_core.py`
- Purpose: Preserves the first two anchor messages (system prompt + user task) while trimming older conversation turns to prevent context window overflow.
- Pattern: Sliding-window turn aggregation.

**Structured Plan Contract (`steps_schema`):**
- Location: `Agent/planner.py`
- Purpose: Enforces strict JSON Schema for step ID, description, and files touched before code execution begins.
- Pattern: Schema validation gate.

## Entry Points

**CLI Interface:**
- Location: `Agent/cli.py:main`
- Invocation: `python Agent/cli.py` or console script `codey` (configured in `pyproject.toml`)
- Responsibilities: Displays ASCII banner, reads user input, handles `/test` and `exit`, runs plan-approve-execute loop.

## Error Handling

**LLM Rate Limiting:**
- Handled in `Agent/agent_core.py` catching `openai.RateLimitError` with up to 5 retries and exponential/linear backoff.

**Tool Execution Failures:**
- Exceptions during tool execution (e.g. `ValueError`, `FileNotFoundError`) are caught in `Agent/agent_core.py` and returned as string error messages (`ERROR: ...`) to the LLM, enabling autonomous self-correction.

**Edit Safety:**
- `replace_edit` enforces exact match count (`count == 1`). If `old_str` matches 0 or >1 times, it raises a descriptive `ValueError` with suggestions.
- `insert_content` enforces target anchor uniqueness before inserting content.

## Cross-Cutting Concerns

**Terminal UX & ANSI Formatting:**
- Encapsulated in `Agent/ui.py` with automatic Windows console ANSI escape enablement (`os.system("")` on `nt`).

**Auditability:**
- Every tool action across any session is logged to `audit_logs/` for tracking and diagnostics.

---

*Architecture analysis: 2026-09-09*\n