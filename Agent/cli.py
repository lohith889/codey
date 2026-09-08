
import json
import shlex
import sys
import uuid

from Agent.agent_core import CODING_SYSTEM_PROMPT, run_agent_loop
from Agent.audit import log_step, render_audit_markdown
from Agent.planner import generate_plan
from Agent.verifier import verify_and_iterate


def run_cli_step() -> bool:
    """Run a single interaction step. Returns False if the session should terminate."""
    task = input("\nTask: ").strip()
    if not task:
        return True
    if task.lower() in ("exit", "quit"):
        print("Exiting.")
        return False

    session_id = uuid.uuid4().hex[:8]

    def on_step(tool_name: str, tool_args: dict, result) -> None:
        log_step(session_id, tool_name, tool_args, result)

    if task.lower() == "/test":
        test_cmd_str = input("Test command to verify (blank to skip): ").strip()
        if test_cmd_str:
            cmd_list = shlex.split(test_cmd_str)
            outcome = verify_and_iterate(cmd_list, on_step=on_step)
            print(f"\nVerification result: {outcome}")
        return True

    print("\nSTRUCTURING PLAN...\n")
    try:
        plan = generate_plan(task)
    except Exception as exc:
        print(f"Error generating plan: {exc}")
        return True

    for step in plan.get("steps", []):
        files = ", ".join(step.get("files_touched", []))
        print(f"{step.get('id', '')}. {step.get('description', '')} ({files})")

    choice = input("\nApprove plan [y/n]: ").strip().lower()
    if choice != "y":
        print("Plan rejected. Task cancelled.")
        return True

    prompt = CODING_SYSTEM_PROMPT + f"""

PLAN:
{json.dumps(plan, indent=2)}

Follow the plan to complete the task.
"""
    print(f"\n[SESSION] Started session: {session_id}")
    try:
        run_agent_loop(task, prompt, on_step=on_step)
    except Exception as exc:
        print(f"Agent error: {exc}")

    print(f"\n[AUDIT] Session log saved to audit_logs/{session_id}.jsonl")
    return True


def main() -> None:
    while True:
        try:
            should_continue = run_cli_step()
            if not should_continue:
                break
        except (KeyboardInterrupt, EOFError):
            print("\nSession interrupted. Exiting.")
            break


if __name__ == "__main__":
    main()