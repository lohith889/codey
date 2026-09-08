import json
from pathlib import Path
import datetime

LOG_DIR = (Path(__file__).resolve().parent.parent / "audit_logs").resolve()
LOG_DIR.mkdir(exist_ok=True)

def log_step(session_id: str, tool_name: str, tool_input: dict, result) -> None:
    entry = {
        'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'tool': tool_name,
        'input': tool_input,
        'result': str(result)[:2000],
    }
    with open(LOG_DIR / f"{session_id}.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def render_audit_markdown(session_id: str) -> str:
    log_file = LOG_DIR / f"{session_id}.jsonl"
    if not log_file.exists():
        return "(no steps logged)"
    lines = [f"# Agent Session {session_id}\n"]
    for raw in log_file.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        e = json.loads(raw)
        lines.append(f"### {e.get('timestamp', '')} - `{e.get('tool', '')}`")
        lines.append(f"**Input:** `{json.dumps(e.get('input', {}))}`\n")
        lines.append(f"**Result:**\n```\n{e.get('result', '')}\n```\n")
    return "\n".join(lines)