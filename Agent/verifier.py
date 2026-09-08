from Agent.agent_core import run_agent_loop, CODING_SYSTEM_PROMPT
from Agent.sandbox import run_sandbox
from typing import Callable, Dict, List, Optional


def verify_and_iterate(
    test_command: List[str],
    max_retries: int = 3,
    on_step: Optional[Callable] = None
) -> Dict:
    """Run a test command and automatically fix failures up to max_retries times."""
    for attempt in range(max_retries):
        print("\n🔍 SANDBOXING...")
        result = run_sandbox(test_command)
        
        if result['exit_code'] == 0:
            print("✅ Tests passed!")
            return {"status": "pass", "attempts": attempt + 1, "result": result}

        print(f"❌ Test failed (attempt {attempt + 1}/{max_retries})")
        print(f"   Exit code: {result['exit_code']}")
        if result['stderr']:
            print(f"   Error: {result['stderr'][:200]}...")

        fix_task = f'''The command `{' '.join(test_command)}` failed.

STDOUT:
{result['stdout']}

STDERR:
{result['stderr']}

Read the relevant file(s), diagnose the failure, and fix the code.
Do not change the tests themselves unless they are clearly wrong.
After fixing, ensure the code runs successfully.
'''
        print("\n🔧 FIXING...")
        run_agent_loop(fix_task, CODING_SYSTEM_PROMPT, on_step=on_step)

    print("\n⚠️  Failed to fix after maximum retries")
    return {'status': 'fail', 'attempts': max_retries, 'result': result}
