import subprocess
from pathlib import Path

ROOT_PATH=Path('./workspace').resolve()

def run_sandbox(command:list,timeout:int = 30)->dict:
    try:
        result=subprocess.run(
            command,
            cwd=ROOT_PATH,
            capture_output=Ture,
            text=True,
            timeout=timeout,
        )

        return{
            "stdout":result.stdout[-4000:],
            "stderr":result.stderr[-4000:],
            "exit_code":result.returncode,
        }

    except:
        return {"stdout":"","stderr":f'Command time out after {timeout}s',"exit_code":-1}