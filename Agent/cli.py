import json
import os
import shlex
import sys
import uuid

from agent_core import CODING_SYSTEM_PROMPT, run_agent_loop
from audit import log_step, render_audit_markdown
from planner import generate_plan
from verifier import verify_and_iterate
import ui


def run_cli_step() -> bool:
    """Run a single interaction step. Returns False if the session should terminate."""
    task = input(f"\n{ui.Colors.BOLD}{ui.Colors.CYAN}Task > {ui.Colors.RESET}").strip()
    if not task:
        return True
    if task.lower() in ("exit", "quit"):
        ui.info("Exiting session.")
        return False

    session_id = uuid.uuid4().hex[:8]

    def on_step(tool_name: str, tool_args: dict, result) -> None:
        log_step(session_id, tool_name, tool_args, result)

    if task.lower() == "/test":
        test_cmd_str = input(f"{ui.Colors.YELLOW}Test command to verify (blank to skip): {ui.Colors.RESET}").strip()
        if test_cmd_str:
            cmd_list = shlex.split(test_cmd_str)
            outcome = verify_and_iterate(cmd_list, on_step=on_step)
            ui.info(f"Verification result: {outcome}")
        return True

    ui.section("PLANNING")
    ui.info("Generating structured execution plan...")
    try:
        plan = generate_plan(task)
    except Exception as exc:
        ui.error(f"Error generating plan: {exc}")
        return True

    ui.print_plan(plan.get("steps", []))

    choice = input(f"{ui.Colors.BOLD}{ui.Colors.YELLOW}Approve plan [y/n]: {ui.Colors.RESET}").strip().lower()
    if choice != "y":
        ui.warning("Plan rejected. Task cancelled.")
        return True

    prompt = CODING_SYSTEM_PROMPT + f"""

PLAN:
{json.dumps(plan, indent=2)}

Follow the plan to complete the task.
"""
    ui.section(f"EXECUTION | Session: {session_id}")
    try:
        run_agent_loop(task, prompt, on_step=on_step)
        ui.success(f"Session {session_id} finished.")
    except Exception as exc:
        ui.error(f"Agent error: {exc}")

    ui.info(f"Session log saved to audit_logs/{session_id}.jsonl")
    return True


def main() -> None:
    model = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")
    ui.banner(model=model, workspace="workspace/")
    while True:
        try:
            should_continue = run_cli_step()
            if not should_continue:
                break
        except (KeyboardInterrupt, EOFError):
            print()
            ui.info("Session interrupted. Exiting.")
            break


if __name__ == "__main__":
    main()