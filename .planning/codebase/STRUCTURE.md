# Codebase Structure

**Analysis Date:** 2026-09-09

## Directory Layout

```
codey/
├── Agent/                  # Core application package
│   ├── agent_core.py       # ReAct agent loop, tool dispatch, and message pruning
│   ├── audit.py            # Session telemetry and JSONL logging
│   ├── cli.py              # CLI entry point, REPL, and user interaction
│   ├── planner.py          # Structured plan generation with JSON schema validation
│   ├── sandbox.py          # Subprocess runner constrained to workspace
│   ├── tools.py            # Sandboxed filesystem and execution tools
│   ├── ui.py               # Terminal UI rendering, colors, and formatting
│   └── verifier.py         # Test verification and iterative repair loop
├── audit_logs/             # Session audit trails (gitignored, auto-created)
│   └── *.jsonl             # Per-session structured event logs
├── tests/                  # Automated test suite (configured for pytest)
├── workspace/              # Dynamic sandbox execution environment (auto-created)
├── .env                    # Local secrets and API credentials (gitignored)
├── .gitignore              # Git ignore rules
├── pyproject.toml          # Project configuration, dependencies, script entry points
├── README.md               # Project overview
└── uv.lock                 # Dependency lockfile
```

## Directory Purposes

**`Agent/`:**
- Purpose: Contains all source code for the Codey coding assistant
- Key files:
  - `cli.py`: Interactive command-line interface and main loop
  - `agent_core.py`: Core agent execution loop, OpenAI client initialization, and tool definitions
  - `planner.py`: Multi-step plan generator using structured output JSON schemas
  - `tools.py`: Tool implementations (`read_file`, `write_file`, `replace_edit`, `insert_content`, `list_dir`, `run_command`)
  - `sandbox.py`: Subprocess execution wrapper with working directory restricted to `workspace/`
  - `verifier.py`: Diagnostic runner and fix loop for automated test execution
  - `audit.py`: Telemetry recorder creating `.jsonl` session traces
  - `ui.py`: Terminal formatting, banners, and status output

**`audit_logs/`:**
- Purpose: Stores immutable, append-only logs for every tool call executed during agent sessions
- Format: JSON Lines files named `{session_id}.jsonl` where `session_id` is an 8-character hex string
- Ignored in git: Excluded from version control via `.gitignore`

**`tests/`:**
- Purpose: Automated test suite directory configured in `pyproject.toml` under `[tool.pytest.ini_options]`
- Current state: Empty directory awaiting unit and integration test coverage

**`workspace/`:**
- Purpose: Isolated sandbox workspace directory where Codey creates, modifies, and tests user code
- Behavior: Dynamically created by `Agent/tools.py` and `Agent/sandbox.py` at runtime; strictly separated from the agent's own source code

## Key File Locations

**Entry Points:**
- `Agent/cli.py`: Main CLI REPL and application entry point
- `pyproject.toml`: Defines console script `codey = "Agent.cli:main"`

**Configuration:**
- `pyproject.toml`: Build system, package dependencies, CLI script entry points, and pytest options
- `.env`: API credentials (`API_KEY`, `GROQ_API_KEY`) and endpoints (`GROQ_BASE_URL`, `MODEL_NAME`)
- `.gitignore`: Files and directories excluded from git tracking

**Core Logic:**
- `Agent/agent_core.py`: ReAct loop, model call, and tool execution dispatch
- `Agent/planner.py`: Planning logic and JSON schema constraints
- `Agent/tools.py`: Safe filesystem operations and diff generation
- `Agent/sandbox.py`: Isolated process execution

**Testing & Verification:**
- `Agent/verifier.py`: Iterative verification and autonomous bug fixing
- `tests/`: Project test suite directory

## Naming Conventions

**Files:**
- Python modules: `snake_case.py` (e.g., `agent_core.py`, `tools.py`)
- Session logs: `{session_id}.jsonl` (8-character hex identifier, e.g., `792c9896.jsonl`)
- Configuration files: standard lowercase or dotfiles (`pyproject.toml`, `.env`, `.gitignore`)

**Functions & Variables:**
- Functions: `snake_case` (e.g., `run_agent_loop`, `_safe_path`, `generate_plan`)
- Variables: `snake_case` (e.g., `session_id`, `tool_name`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `CODING_SYSTEM_PROMPT`, `TOOLS`, `ROOT_PATH`)
- Private helpers: Leading underscore (e.g., `_safe_path`, `_group_into_turns`)

**Classes:**
- Classes: `PascalCase` (e.g., `Colors`)

## Where to Add New Code

**New Tool:**
1. Define tool signature and schema in `Agent/agent_core.py:TOOLS`
2. Implement tool logic in `Agent/tools.py`
3. Map tool function in `Agent/agent_core.py:TOOL_FUNCTIONS`
4. Update `Agent/agent_core.py:CODING_SYSTEM_PROMPT` with usage rules

**New CLI Command or Mode:**
- Add command handling in `Agent/cli.py:run_cli_step`

**New Unit & Integration Tests:**
- Add test modules to `tests/` following the `test_*.py` pattern (e.g., `tests/test_tools.py`, `tests/test_planner.py`)

**UI Enhancements:**
- Add styling functions and helpers in `Agent/ui.py`

---

*Structure analysis: 2026-09-09*\n