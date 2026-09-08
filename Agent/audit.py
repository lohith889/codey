import json
from pathlib import Path
import datetime
from typing import Any, Dict

LOG_DIR = Path('./audit_logs')
LOG_DIR.mkdir(exist_ok=True)


def log_step(session_id: str, tool_name: str, tool_input: Dict, result: Any) -> None:
    """Log a single agent step to the audit log."""
    entry = {
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'tool': tool_name,
        'input': tool_input,
        'result': str(result)[:2000],
    }
    with open(LOG_DIR / f"{session_id}.jsonl", "a") as f:
        f.write(json.dumps(entry) + "\n")


def render_audit_markdown(session_id: str) -> str:
    """Render the audit log for a session as a Markdown report."""
    log_file = LOG_DIR / f"{session_id}.jsonl"
    if not log_file.exists():
        return "(no steps logged)"
    
    lines = [f"# Agent Session {session_id}\n"]
    for raw in log_file.read_text().splitlines():
        e = json.loads(raw)
        lines.append(f"### {e['timestamp']} - `{e['tool']}`")
        lines.append(f"**Input:** `{json.dumps(e.get('input', {}))}`\n")
        lines.append(f"**Result:**\n```\n{e['result']}\n```\n")
    return "\n".join(lines)