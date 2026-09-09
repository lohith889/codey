# Requirements: Codey

**Defined:** 2026-09-09
**Core Value:** Reliable, user-supervised autonomous code editing and verification that operates safely inside a sandboxed workspace without corrupting user repositories.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Foundation & Packaging

- [ ] **FOUND-01**: User can run `codey` as an installed package without `ModuleNotFoundError` by refactoring unqualified imports in `Agent/` and adding `Agent/__init__.py`
- [ ] **FOUND-02**: Developer can run `pytest` with a passing baseline test suite covering `Agent/tools.py`, `Agent/sandbox.py`, and `Agent/agent_core.py`

### Interactive Plan Editing

- [ ] **PLAN-01**: User can interactively edit, add, remove, or reorder proposed plan steps before execution begins
- [ ] **PLAN-02**: User can submit feedback to have the planner re-generate or adjust specific steps

### Multi-File Diff Review

- [ ] **DIFF-01**: Agent stages proposed edits across all touched files before writing to the workspace
- [ ] **DIFF-02**: User can view a unified colored diff preview across all modified files and approve or reject the change set before files are modified on disk

### Streaming Token Output

- [ ] **STREAM-01**: User sees real-time token streaming for model thoughts and responses in the terminal UI instead of waiting for full completions
- [ ] **STREAM-02**: Terminal output maintains clean ANSI formatting, spinner transitions, and tool-call boundary rendering during live streams

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Provider Flexibility

- **PROV-01**: Support local LLMs via Ollama / vLLM with custom context window sizing
- **PROV-02**: Support native Anthropic Claude API provider

### Extended Agent Capabilities

- **EXT-01**: Persistent multi-workspace management
- **EXT-02**: Token usage metrics and cost estimation per session

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Web GUI / Browser interface | Codey is strictly designed for terminal developers; web UI introduces heavy frontend stack overhead |
| Cloud telemetry / remote logging | Audit trails are strictly local for developer privacy and offline safety |
| Multi-agent swarm orchestration | Single orchestrator loop ensures deterministic debugging and lower token consumption |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| FOUND-01 | Phase 1 | Pending |
| FOUND-02 | Phase 1 | Pending |
| PLAN-01 | Phase 2 | Pending |
| PLAN-02 | Phase 2 | Pending |
| DIFF-01 | Phase 3 | Pending |
| DIFF-02 | Phase 3 | Pending |
| STREAM-01 | Phase 4 | Pending |
| STREAM-02 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0

---
*Requirements defined: 2026-09-09*
*Last updated: 2026-09-09 after initialization*
