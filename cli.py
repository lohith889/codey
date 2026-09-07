
def main():
    from agent_core import run_agent_loop,CODING_SYSTEM_PROMPT
    from planner import generate_plan
    import sys

    task=input("Task:").strip()
    if(task.lower()=="exit"):
        sys.exit('Cancelled.')

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