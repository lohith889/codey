# Codey

## What This Is

Codey is an autonomous AI pair-programming assistant built in Python that translates high-level developer tasks into structured execution plans and executes them using sandboxed filesystem and terminal tools. Designed for terminal-centric workflows, Codey enables developers to safely delegate multi-step coding, refactoring, and test-driven bug fixing tasks with human-in-the-loop supervision.

## Core Value

Reliable, user-supervised autonomous code editing and verification that operates safely inside a sandboxed workspace without corrupting user repositories.

## Requirements

### Validated

- ✓ Plan generation via structured JSON schema with OpenAI/Groq models — existing (`Agent/planner.py`)
- ✓ ReAct tool-calling execution loop with turn-based context pruning — existing (`Agent/agent_core.py`)
- ✓ Workspace-confined file operations (`read_file`, `write_file`, `replace_edit`, `insert_content`, `list_dir`) — existing (`Agent/tools.py`)
- ✓ Sandboxed subprocess command execution with timeout and cross-platform handling — existing (`Agent/sandbox.py`)
- ✓ Autonomous test verification and iterative self-repair loop (`/test`) — existing (`Agent/verifier.py`)
- ✓ Per-session append-only JSONL audit logging — existing (`Agent/audit.py`)
- ✓ ANSI terminal UI with banners, formatted plans, and tool call progress — existing (`Agent/ui.py`)

### Active

- [ ] Package import cleanup: Refactor internal imports in `Agent/` to package-relative/qualified imports and add `Agent/__init__.py` so the `codey` console script runs reliably as an installed package
- [ ] Comprehensive test suite: Implement unit and integration tests with `pytest` covering filesystem tools, sandboxing, message pruning, and verification logic in `tests/`
- [ ] Interactive plan editing: Allow users to inspect, modify, add, or reject individual steps in proposed plans interactively before execution begins
- [ ] Multi-file diff review: Stage proposed changes across multiple files and display unified diffs for user confirmation prior to committing edits to the workspace filesystem
- [ ] Real-time streaming token output: Stream assistant thinking and response tokens directly to the terminal UI for instant responsiveness

### Out of Scope

- Web GUI / browser interface — Codey is strictly a focused, lightweight terminal CLI
- Cloud telemetry / remote logging — All audit logs remain local in `audit_logs/` for privacy and offline reliability
- Multi-agent swarm orchestration — Single orchestrator with dedicated tool execution is prioritized for predictability

## Context

- Python 3.11+ application managed with `uv` and `pyproject.toml`
- Core LLM integration uses OpenAI SDK with Groq API endpoint (`GROQ_BASE_URL`, `MODEL_NAME`)
- Codebase was reorganized into `Agent/` which left internal module imports un-prefixed, breaking package execution
- `tests/` directory is currently empty, needing test harness and fixtures

## Constraints

- **Tech stack**: Python >=3.11, `openai>=1.0.0`, `python-dotenv>=1.0.0`, `pytest>=8.0.0`
- **Security**: Strict filesystem boundary enforcement keeping all agent edits within `workspace/`
- **Platform**: Cross-platform compatibility for Windows (PowerShell/cmd) and POSIX systems

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Combine UX & foundation into one milestone | Package import fixes and test harness provide necessary stability to build and verify interactive plan editing and diff review | — Pending |
| Interactive plan editing before execution | Empowers user to steer agent strategy without re-running full LLM prompt loops | — Pending |
| Multi-file diff review staging | Prevents partial or destructive writes before user validates total change set | — Pending |
| Real-time streaming output | Minimizes perceived latency during lengthy LLM generation turns | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-09 after initialization*
