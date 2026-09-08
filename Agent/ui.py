import os
import sys

# Enable ANSI escape sequences on Windows console
if os.name == "nt":
    os.system("")

class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

def banner(model: str = "", workspace: str = ""):
    width = 68
    border = "=" * width
    print(f"{Colors.CYAN}{border}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BRIGHT_WHITE}  CODEY | Autonomous Coding Assistant{Colors.RESET}")
    if model:
        print(f"  {Colors.DIM}Model:{Colors.RESET}     {Colors.WHITE}{model}{Colors.RESET}")
    if workspace:
        print(f"  {Colors.DIM}Workspace:{Colors.RESET} {Colors.WHITE}{workspace}{Colors.RESET}")
    print(f"{Colors.CYAN}{border}{Colors.RESET}\n")

def section(title: str):
    bar = "-" * max(2, 64 - len(title))
    print(f"\n{Colors.CYAN}--- [{title}] {bar}{Colors.RESET}")

def print_plan(steps: list):
    width = 68
    border = "+" + "-" * (width - 2) + "+"
    print(f"\n{Colors.CYAN}{border}{Colors.RESET}")
    title = "PROPOSED EXECUTION PLAN"
    pad = width - 4 - len(title)
    print(f"{Colors.CYAN}|{Colors.RESET} {Colors.BOLD}{title}{Colors.RESET}" + " " * pad + f"{Colors.CYAN}|{Colors.RESET}")
    print(f"{Colors.CYAN}{border}{Colors.RESET}")
    for step in steps:
        step_id = step.get("id", "")
        desc = step.get("description", "")
        files = ", ".join(step.get("files_touched", []))
        print(f"{Colors.CYAN}|{Colors.RESET} {Colors.BOLD}[Step {step_id}]{Colors.RESET} {desc}")
        if files:
            print(f"{Colors.CYAN}|{Colors.RESET}   {Colors.DIM}Files: {files}{Colors.RESET}")
    print(f"{Colors.CYAN}{border}{Colors.RESET}\n")

def thinking(iteration: int, max_iter: int):
    print(f"{Colors.DIM}[THINKING]{Colors.RESET} Step {iteration:02d}/{max_iter:02d} | Generating response...")

def tool_call(tool_name: str, args: dict | None):
    print(f"\n{Colors.YELLOW}[TOOL CALL]{Colors.RESET} {Colors.BOLD}{tool_name}{Colors.RESET}")
    if args:
        for k, v in args.items():
            val_str = str(v)
            if len(val_str) > 90:
                val_str = val_str[:87] + "..."
            val_str = val_str.replace("\n", " \\n ")
            print(f"  {Colors.DIM}-> {k}:{Colors.RESET} {val_str}")

def tool_result(result_text: str):
    res = str(result_text).strip()
    if not res:
        print(f"  {Colors.GREEN}<= (done / no output){Colors.RESET}")
        return

    lines = res.splitlines()
    if "ERROR" in lines[0] or "Error" in lines[0] or "Exception" in lines[0]:
        print(f"  {Colors.RED}<= [ERROR] {lines[0]}{Colors.RESET}")
        for l in lines[1:4]:
            print(f"     {Colors.RED}{l}{Colors.RESET}")
    else:
        print(f"  {Colors.GREEN}<= {lines[0]}{Colors.RESET}")
        for l in lines[1:3]:
            print(f"     {Colors.DIM}{l}{Colors.RESET}")
        if len(lines) > 3:
            print(f"     {Colors.DIM}... ({len(lines) - 3} more lines){Colors.RESET}")

def assistant_response(content: str):
    print(f"\n{Colors.GREEN}[ASSISTANT]{Colors.RESET}")
    print(f"{content}\n")

def info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET} {msg}")

def success(msg: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.RESET} {msg}")

def warning(msg: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.RESET} {msg}")

def error(msg: str):
    print(f"{Colors.RED}[ERROR]{Colors.RESET} {msg}")
