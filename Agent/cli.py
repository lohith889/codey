
def main():
    from Agent.agent_core import run_agent_loop,CODING_SYSTEM_PROMPT
    from Agent.planner import generate_plan
    import sys
    from Agent.verifier import verify_and_iterate
    from audit import log_step, render_audit_markdown
    import uuid

    task=input("Task:").strip()
    if(task.lower()=="exit"):
        sys.exit('Cancelled.')
    if(task.lower()=="/test"):
        test_cmd=input("\Test command to verify (blank to skip): ").strip()
        if test_cmd:
            outcome=verify_and_iterate(test_cmd,on_step=on_step)
            print(f"\n Verification result: {outcome}")
        main()

    print("STRUCTURING PLAN...\n")
    plan=generate_plan(task)
    for step in plan["steps"]:
        print(f"{step['id']}. {step['description']}) ({', '.join(step['files_touched'])})")
    if input("\nAprove plan[y/n]").strip().lower() !='y':
        sys.exit('Cancelled.')

    CODING_SYSTEM_PROMPT+=f'''
    PLAN:
    {plan}

    follow the plan to complete the taks.
    '''
    run_agent_loop(task,CODING_SYSTEM_PROMPT)


if __name__=="__main__":
    while(True):
        main()