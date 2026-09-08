import shlex
from agent_core import CODING_SYSTEM_PROMPT, run_agent_loop
from sandbox import run_sandbox


def verify_and_iterate(
    test_command: list | str, max_retries: int = 3, on_step=None
) -> dict:
    if isinstance(test_command, str):
        test_command = shlex.split(test_command)

    command_str = " ".join(test_command)

    for attempt in range(max_retries):
        print("\nSANDBOXING...")
        result = run_sandbox(test_command)
        if result["exit_code"] == 0:
            return {"status": "pass", "attempts": attempt + 1}

        fix_task = f"""The command `{command_str}` failed with exit code {result['exit_code']}.

STDOUT:
{result['stdout']}

STDERR:
{result['stderr']}

Read the relevant file(s), diagnose the failure, and fix the code.
Do not change the tests themselves unless they are clearly wrong.
"""
        print("\nFIXING...")
        run_agent_loop(fix_task, CODING_SYSTEM_PROMPT, on_step=on_step)

    return {"status": "fail", "attempts": max_retries}