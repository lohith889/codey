#!/usr/bin/env python3
"""Command-line interface for the coding agent."""

import sys
import uuid
from pathlib import Path


def print_header():
    """Print a nice header for the CLI."""
    print("\n" + "=" * 60)
    print("       🤖 CODING AGENT - Autonomous Code Assistant")
    print("=" * 60)


def print_plan(plan: dict):
    """Display the generated plan in a formatted way."""
    print("\n📋 PROPOSED PLAN:")
    print("-" * 40)
    
    for step in plan["steps"]:
        files = ", ".join(step["files_touched"]) if step["files_touched"] else "(no files)"
        print(f"  {step['id']}. {step['description']}")
        print(f"     📁 Files: {files}")
    
    print(f"\n✅ Completion Criteria:")
    print(f"   {plan.get('completion_criteria', 'Not specified')}")
    print("-" * 40)


def on_step_callback(tool_name: str, args: dict, result: str):
    """Callback function to log each step during execution."""
    from Agent.audit import log_step
    
    session_id = getattr(on_step_callback, 'session_id', 'default')
    log_step(session_id, tool_name, args, result)


def main():
    """Main entry point for the CLI."""
    from Agent.agent_core import run_agent_loop, CODING_SYSTEM_PROMPT
    from Agent.planner import generate_plan
    from Agent.verifier import verify_and_iterate
    from Agent.audit import log_step, render_audit_markdown
    
    print_header()
    
    # Generate a unique session ID for this run
    session_id = str(uuid.uuid4())[:8]
    on_step_callback.session_id = session_id
    print(f"\n🆔 Session ID: {session_id}")
    
    while True:
        print("\n" + "-" * 40)
        task = input("\n💬 Task (or 'exit' to quit, '/test' to run tests): ").strip()
        
        if task.lower() == "exit":
            print("\n👋 Goodbye!")
            sys.exit(0)
        
        if not task:
            continue
        
        if task.lower() == "/test":
            test_cmd = input("\n🧪 Test command to verify (blank to skip): ").strip()
            if test_cmd:
                outcome = verify_and_iterate(
                    test_cmd.split(),
                    max_retries=3,
                    on_step=on_step_callback
                )
                print(f"\n📊 Verification Result: {outcome['status']}")
                print(f"   Attempts: {outcome['attempts']}")
            continue
        
        # Generate and display plan
        print("\n📋 STRUCTURING PLAN...")
        try:
            plan = generate_plan(task)
            print_plan(plan)
        except Exception as e:
            print(f"❌ Error generating plan: {e}")
            print("Proceeding without a formal plan...")
            plan = {"steps": [], "completion_criteria": ""}
        
        # Get approval for the plan
        approval = input("\n✅ Approve plan? [y/n]: ").strip().lower()
        if approval != 'y':
            print("\n❌ Plan cancelled.")
            continue
        
        # Enhance system prompt with the plan
        enhanced_prompt = CODING_SYSTEM_PROMPT
        if plan.get("steps"):
            enhanced_prompt += f"""

EXECUTION PLAN:
{plan}

Follow this plan step by step to complete the task.
Report progress after completing each step.
"""
        
        # Run the agent
        print("\n🚀 EXECUTING TASK...\n")
        try:
            result = run_agent_loop(
                task=task,
                system_prompt=enhanced_prompt,
                max_iter=50,
                on_step=on_step_callback
            )
            print("\n✅ Task execution completed!")
        except RuntimeError as e:
            print(f"\n⚠️  {e}")
        
        # Show audit summary
        print("\n📝 AUDIT SUMMARY:")
        print("-" * 40)
        audit_log = LOG_DIR / f"{session_id}.jsonl"
        if audit_log.exists():
            step_count = sum(1 for _ in open(audit_log))
            print(f"   Total steps logged: {step_count}")
            print(f"   Log file: {audit_log}")
        else:
            print("   No steps logged")
        print("-" * 40)


if __name__ == "__main__":
    from pathlib import Path
    LOG_DIR = Path('./audit_logs')
    LOG_DIR.mkdir(exist_ok=True)
    main()
