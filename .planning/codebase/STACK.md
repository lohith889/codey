# Technology Stack

**Analysis Date:** 2026-09-09

## Languages

**Primary:**
- Python 3.11+ (verified runtime: Python 3.11.9) - All application code including planning, execution engine, CLI, sandboxing, and audit logging in `Agent/`

**Secondary:**
- None (pure Python project)

## Runtime

**Environment:**
- Python 3.11.9 (CPython)
- Cross-platform support for Windows and POSIX systems. Specifically includes Windows console ANSI escape sequence initialization in `Agent/ui.py` and `subprocess.list2cmdline` command serialization in `Agent/sandbox.py`

**Package Manager:**
- `uv` (v0.12.5)
- Lockfile: `uv.lock` present and tracked in version control

## Frameworks

**Core:**
- None (custom lightweight autonomous agent engine built on Python standard library and OpenAI SDK)

**Testing:**
- `pytest` (v9.1.1, specified as `>=8.0.0` in `pyproject.toml`) configured via `[tool.pytest.ini_options]` in `pyproject.toml`

**Build/Dev:**
- `uv_build` (v0.12.5, `>=0.12.5,<0.13.0`) as build-backend in `pyproject.toml`
- `python-dotenv` (v1.0.0+) for environment variable loading from `.env`

## Key Dependencies

**Critical:**
- `openai>=1.0.0` - Powers model completions, structured JSON schema response enforcement in `Agent/planner.py`, and ReAct tool-calling loops in `Agent/agent_core.py`
- `python-dotenv>=1.0.0` - Automatically loads local environment configuration and API credentials in `Agent/agent_core.py` and `Agent/planner.py`
- `pytest>=8.0.0` - Test discovery and execution engine

**Infrastructure (Standard Library):**
- `pathlib.Path` - Path manipulation and strict workspace boundary validation in `Agent/tools.py` and `Agent/sandbox.py`
- `subprocess` - Isolated child process execution inside `workspace/` in `Agent/sandbox.py`
- `difflib` - Unified diff generation for file edits and insertions in `Agent/tools.py`
- `json` - Tool arguments parsing and structured plan serialization
- `shlex` - Safe POSIX/Windows command string parsing in `Agent/cli.py`, `Agent/tools.py`, and `Agent/verifier.py`
- `uuid` & `datetime` - Unique session ID generation and ISO UTC audit logging in `Agent/audit.py`

## Configuration

**Environment:**
- Configured via `.env` file (loaded via `dotenv.load_dotenv()`)
- Key environment variables:
  - `API_KEY` or `GROQ_API_KEY`: Authentication key for model completions
  - `GROQ_BASE_URL`: OpenAI-compatible endpoint URL (defaults to `https://api.groq.com/openai/v1`)
  - `MODEL_NAME`: Core coding agent model identifier (defaults to `openai/gpt-oss-20b`)
  - `PLANNER_MODEL_NAME`: Planning model identifier (falls back to `MODEL_NAME` or `openai/gpt-oss-20b`)

**Build:**
- `pyproject.toml` - Project packaging metadata, dependencies, entry point script `codey = "Agent.cli:main"`, and pytest testpaths

## Platform Requirements

**Development:**
- Windows / macOS / Linux with Python >=3.11
- `uv` recommended for environment isolation and dependency resolution
- Valid OpenAI/Groq compatible API key in `.env`

**Production:**
- CLI application executable via `python Agent/cli.py` or entry point script `codey`
- Runtime workspace dynamically created at `workspace/` relative to project root

---

*Stack analysis: 2026-09-09*
*Update after major dependency changes*\n