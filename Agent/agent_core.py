from Agent.tools import read_file, write_file, edit_file, list_dir, run_command
from openai import OpenAI
from dotenv import load_dotenv
import os
import json


load_dotenv()

def get_client() -> OpenAI:
    api_key = os.getenv("GROQ_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        raise ValueError(
            "No API key found. Please set GROQ_API_KEY or API_KEY in your environment or .env file."
        )
    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    return OpenAI(api_key=api_key, base_url=base_url)

CODING_SYSTEM_PROMPT = """
You are a careful coding agent working inside a project directory.

RULES:
- You have access to tools: read_file, write_file, edit_file, list_dir, run_command
- Use these tools to interact with files and verify code execution
- Do NOT generate code in your response - use write_file instead
- Use run_command to run scripts, execute tests, or check code inside the workspace
- For write_file, provide path and content as JSON
- For edit_file, provide path, old_str, and new_str
- For read_file, provide path only
- Once task is over stop tool calling

TOOL CALL FORMAT:
When using a tool, provide the arguments in valid JSON format.
Example: write_file({"path": "hello.py", "content": "print('Hello')"})

RESPONSE FORMAT:
- If you need to explain something, do it in the content field
- Then use the tool calls to actually do the work
- Never output raw code unless it's inside a tool call

Always verify your changes by reading the file after editing.
"""


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Replace one exact string in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "old_str": {"type": "string"},
                    "new_str": {"type": "string"}
                },
                "required": ["path", "old_str", "new_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List files in a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"}
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command inside the workspace directory (e.g. 'python test.py').",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command line string to run."
                    }
                },
                "required": ["command"]
            }
        }
    }
]

TOOL_FUNCTIONS = {
    "read_file": lambda args: read_file(args["path"]),
    "write_file": lambda args: write_file(args["path"], args["content"]),
    "edit_file": lambda args: edit_file(
        args["path"], args["old_str"], args["new_str"]
    ),
    "list_dir": lambda args: list_dir(args.get("path", ".")),
    "run_command": lambda args: run_command(args["command"]),
}


def _group_into_turns(messages: list) -> list:
    """Group non-anchor messages into atomic conversation turns."""
    turns = []
    current_turn = []
    for msg in messages:
        role = msg.get("role")
        if role == "assistant" and current_turn:
            turns.append(current_turn)
            current_turn = [msg]
        else:
            current_turn.append(msg)
    if current_turn:
        turns.append(current_turn)
    return turns


def prune_messages(messages: list, max_messages: int = 20) -> list:
    """Prune conversation history while preserving anchors and tool call integrity."""
    if len(messages) <= max_messages:
        return messages

    anchors = messages[:2]
    history = messages[2:]
    turns = _group_into_turns(history)

    while len(turns) > 1 and (len(anchors) + sum(len(t) for t in turns)) > max_messages:
        turns.pop(0)

    pruned = anchors[:]
    for turn in turns:
        pruned.extend(turn)
    return pruned


def run_agent_loop(
    task: str,
    system_prompt: str,
    max_iter: int = 50,
    max_messages: int = 20,
    on_step=None,
) -> str:
    client = get_client()
    model = os.getenv("MODEL_NAME", "openai/gpt-oss-20b")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]

    for iteration in range(max_iter):
        print("THINKING...\n")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print("\nAssistant:\n")
            print(message.content)
            return message.content or ""

        messages.append({
            "role": "assistant",
            "content": message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in message.tool_calls
            ],
        })

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            print(f"\n[TOOL] {tool_name}")

            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as err:
                args = None
                result = f"ERROR: Invalid JSON arguments: {err}"
            else:
                try:
                    if tool_name not in TOOL_FUNCTIONS:
                        result = f"ERROR: Unknown tool '{tool_name}'"
                    else:
                        result = TOOL_FUNCTIONS[tool_name](args)
                except Exception as exc:
                    result = f"ERROR: {exc}"

            if on_step and args is not None:
                on_step(tool_name, args, result)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": str(result),
            })

        messages = prune_messages(messages, max_messages=max_messages)

    raise RuntimeError(f"Hit max iterations ({max_iter})")
