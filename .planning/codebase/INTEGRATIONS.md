# External Integrations

**Analysis Date:** 2026-09-09

## APIs & External Services

**LLM Provider (Groq / OpenAI Compatible):**
- Service: Groq API or generic OpenAI-compatible completion service
  - SDK/Client: `openai.OpenAI` client (v1.0.0+) initialized in `Agent/agent_core.py:get_client` and reused in `Agent/planner.py`
  - Auth: API key supplied via `GROQ_API_KEY` or `API_KEY` environment variables
  - Base URL: Configured via `GROQ_BASE_URL`, defaulting to `https://api.groq.com/openai/v1`
  - Endpoints used:
    - `/chat/completions` (with function tool calling and `tool_choice="auto"`) in `Agent/agent_core.py`
    - `/chat/completions` (with `response_format={"type": "json_schema", ...}` for structured step generation) in `Agent/planner.py`
  - Models:
    - Execution agent model: `MODEL_NAME` (default: `openai/gpt-oss-20b`)
    - Planning model: `PLANNER_MODEL_NAME` (fallback: `MODEL_NAME`, default: `openai/gpt-oss-20b`)
  - Error Handling & Resilience:
    - Rate limit backoff: `openai.RateLimitError` triggers up to 5 retries with linear backoff (2.0s, 4.0s, 6.0s, 8.0s, 10.0s) in `Agent/agent_core.py`
    - Plan retry loop: Up to 3 retry attempts with feedback messages on JSON decode or schema validation failures in `Agent/planner.py`

## Data Storage

**Databases:**
- None (no relational or NoSQL database required)

**File Storage & Telemetry:**
- Audit Logging: Append-only JSONL files written to `audit_logs/{session_id}.jsonl` via `Agent/audit.py`
  - Each entry captures UTC timestamp, tool name, input arguments, and truncated result (up to 2000 characters)
- Workspace Files: All user project files created or modified by the agent are stored in the isolated `workspace/` directory
  - Boundary enforced by `Agent/tools.py:_safe_path` using `Path.is_relative_to(ROOT_PATH)`

**Caching:**
- None (conversation messages are held in-memory and pruned via `Agent/agent_core.py:prune_messages` with `max_messages=20`)

## Authentication & Identity

**Auth Provider:**
- No user authentication system (standalone local developer CLI)
- External service authentication relies solely on API keys passed via environment variables

## Monitoring & Observability

**Error Tracking:**
- Local console output using ANSI color sequences via `Agent/ui.py` (`ui.error`, `ui.warning`, `ui.info`, `ui.success`)
- Terminal status indicators for thinking iterations, tool executions, and diff results

**Audit Trail:**
- Structured JSONL logging in `audit_logs/` providing complete reproducibility of tool calls and agent reasoning per session ID

**Logs:**
- Standard output (`stdout`) and standard error (`stderr`) formatted through `Agent/ui.py`
- Sandbox subprocess execution captures the last 4000 characters of stdout and stderr in `Agent/sandbox.py`

## CI/CD & Deployment

**Hosting:**
- Local CLI tool; no cloud hosting infrastructure

**CI Pipeline:**
- None configured in repository yet; test discovery configured for pytest in `pyproject.toml`

## Environment Configuration

**Development:**
- Required environment variable:
  - `API_KEY` or `GROQ_API_KEY`: API credential for LLM service
- Optional environment variables:
  - `GROQ_BASE_URL`: Custom API base URL
  - `MODEL_NAME`: Custom model name for execution
  - `PLANNER_MODEL_NAME`: Custom model name for planning
- Configuration files:
  - `.env`: Gitignored file for local secrets
  - `.gitignore`: Ignores `.env`, `audit_logs/`, `workspace/`, `__pycache__/`, `.venv/`

**Production:**
- Packaging via `pyproject.toml` and `uv_build`
- Executed locally via CLI: `codey` or `python Agent/cli.py`

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

---

*Integrations analysis: 2026-09-09*\n