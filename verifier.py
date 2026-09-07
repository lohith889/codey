from agent_core import run_agent_loop,CODING_SYSTEM_PROMPT
from sandbox import run_sandbox

def verify_and_iterate(test_command:list,maxretires:int=3,on_step=None)->dict:
    for attempt in range(maxretires):
        result=run_sandbox(test_command)
        if result['exit_code']==0:
            return {"status":"pass","attempts":attempt+1}

        fix_task=f'''the command `{' '.join(test_command)}` failed
        STDOUT:
        {result['stdout']}
        STDERR:
        {result['stderr']}

    Read the relevant file(s), diagnose the fialure, and fix the code.
    Do not change the tests themselves unless they are clearly wrong
    '''

        run_agent_loop(fix_task,CODING_SYSTEM_PROMPT,on_step=on_step)

    return {'status':'fail','attempts':maxretires}