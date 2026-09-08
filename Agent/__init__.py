"""
Coding Agent - A simple autonomous coding assistant.

This package provides a framework-free coding agent that can:
- Plan and execute coding tasks
- Read, write, and edit files
- Run and verify code in a sandbox
- Log all actions for audit purposes
"""

__version__ = "1.0.0"
__author__ = "Coding Agent Team"

# Lazy imports to avoid API key requirement at import time
def __getattr__(name):
    if name == "run_agent_loop":
        from Agent.agent_core import run_agent_loop
        return run_agent_loop
    elif name == "CODING_SYSTEM_PROMPT":
        from Agent.agent_core import CODING_SYSTEM_PROMPT
        return CODING_SYSTEM_PROMPT
    elif name == "generate_plan":
        from Agent.planner import generate_plan
        return generate_plan
    elif name == "read_file":
        from Agent.tools import read_file
        return read_file
    elif name == "write_file":
        from Agent.tools import write_file
        return write_file
    elif name == "edit_file":
        from Agent.tools import edit_file
        return edit_file
    elif name == "list_dir":
        from Agent.tools import list_dir
        return list_dir
    elif name == "run_sandbox":
        from Agent.sandbox import run_sandbox
        return run_sandbox
    elif name == "verify_and_iterate":
        from Agent.verifier import verify_and_iterate
        return verify_and_iterate
    elif name == "log_step":
        from Agent.audit import log_step
        return log_step
    elif name == "render_audit_markdown":
        from Agent.audit import render_audit_markdown
        return render_audit_markdown
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = [
    "run_agent_loop",
    "CODING_SYSTEM_PROMPT",
    "generate_plan",
    "read_file",
    "write_file",
    "edit_file",
    "list_dir",
    "run_sandbox",
    "verify_and_iterate",
    "log_step",
    "render_audit_markdown",
]
