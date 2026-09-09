# Roadmap: Codey

## Overview

Codey evolves from a standalone prototype script into a hardened, developer-friendly autonomous pair-programmer. The roadmap begins with package foundation and automated test harness, then implements user-steering capabilities (interactive plan editing), safety barriers (multi-file diff review before disk modification), and ends with real-time responsiveness (streaming token output).

## Phases

- [x] **Phase 1: Foundation & Test Infrastructure** - Fix package import resolution, package entry point, and establish automated unit/integration test suite. (completed 2026-09-09)
- [ ] **Phase 2: Interactive Plan Editing** - Enable users to inspect, modify, reorder, add, or reject individual steps in proposed execution plans.
- [ ] **Phase 3: Multi-File Diff Staging & Review** - Stage multi-file edits before writing to disk and present unified diffs for explicit user approval.
- [ ] **Phase 4: Real-Time Streaming Output** - Stream assistant reasoning and output tokens live in the terminal with clean ANSI UX.

## Phase Details

### Phase 1: Foundation & Test Infrastructure

**Goal**: Package import cleanup and automated test harness ensuring Codey runs as an installed CLI and core tools are verified.
**Mode:** mvp
**Depends on**: Nothing
**Requirements**: FOUND-01, FOUND-02
**Success Criteria** (what must be TRUE):

  1. `python -m Agent.cli` and `codey` entry point run without `ModuleNotFoundError`.
  2. `pytest` executes and passes all test modules in `tests/`.
  3. Core workspace tools (`read_file`, `write_file`, `replace_edit`, `insert_content`, `run_sandbox`) have passing unit tests.

**Plans**: 2 plans

Plans:

- [x] 01-01: Fix package structure and module imports in `Agent/` and verify `codey` CLI entry point.
- [x] 01-02: Implement unit test suite with pytest covering tools, sandboxing, and agent message pruning.

### Phase 2: Interactive Plan Editing

**Goal**: Interactive step customization allowing users to guide and adjust execution strategies before tools are invoked.
**Mode:** mvp
**Depends on**: Phase 1
**Requirements**: PLAN-01, PLAN-02
**Success Criteria** (what must be TRUE):

  1. CLI displays an interactive menu to edit descriptions, add steps, or delete steps before plan approval.
  2. User can request AI plan revision with custom guidance prompt.
  3. Modified plan accurately guides subsequent `run_agent_loop` execution.

**Plans**: 2 plans

Plans:

- [ ] 02-01: Implement interactive CLI step editor with add, edit, remove, and reorder options.
- [ ] 02-02: Implement planner feedback loop for AI-driven re-prompting and schema validation.

### Phase 3: Multi-File Diff Staging & Review

**Goal**: Safe multi-file edit review staging so users can inspect unified diffs before any changes land on disk.
**Mode:** mvp
**Depends on**: Phase 2
**Requirements**: DIFF-01, DIFF-02
**Success Criteria** (what must be TRUE):

  1. File modifications during tool execution are staged in memory/cache rather than writing immediately to disk.
  2. A colored multi-file unified diff preview is displayed in the terminal.
  3. User can explicitly approve to apply edits or reject to discard all staged changes.

**Plans**: 2 plans

Plans:

- [ ] 03-01: Implement workspace staging layer for file edits and writes.
- [ ] 03-02: Build multi-file unified diff renderer in terminal UI with approval gate.

### Phase 4: Real-Time Streaming Output

**Goal**: Instant feedback via streaming LLM reasoning and response tokens in the terminal UI.
**Mode:** mvp
**Depends on**: Phase 3
**Requirements**: STREAM-01, STREAM-02
**Success Criteria** (what must be TRUE):

  1. Model responses stream live token-by-token in the terminal.
  2. Thinking blocks and tool call boundaries transition cleanly without ANSI corruption.
  3. Streaming maintains full compatibility with rate limit retries and audit logging.

**Plans**: 2 plans

Plans:

- [ ] 04-01: Implement streaming completion handler and token display loop in `Agent/agent_core.py`.
- [ ] 04-02: Refine terminal UI transitions, spinners, and tool call rendering during streaming.

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation & Test Infrastructure | 2/2 | Complete    | 2026-09-09 |
| 2. Interactive Plan Editing | 0/2 | Not started | - |
| 3. Multi-File Diff Staging & Review | 0/2 | Not started | - |
| 4. Real-Time Streaming Output | 0/2 | Not started | - |\n
