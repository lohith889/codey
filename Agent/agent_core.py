from tools import (
    read_file,
    write_file,
    replace_edit,
    insert_content,
    edit_file,
    list_dir,
    run_command,
)
from openai import OpenAI, RateLimitError
from dotenv import load_dotenv
import os
import json
import time
import ui


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
- You have access to tools: read_file, write_file, replace_edit, insert_content, list_dir, run_command
- Use these tools to interact with files and verify code execution
- Do NOT generate code in your response - use write_file, replace_edit, or insert_content instead
- Use run_command to run scripts, execute tests, or check code inside the workspace
- Once task is complete, stop tool calling and provide a final summary

CRITICAL TOOL CALL FORMAT:
When calling a tool, your response MUST follow this exact JSON structure:

{
  "name": "tool_name",
  "arguments": "{\"param1\": \"value1\", \"param2\": \"value2\"}"
}

IMPORTANT RULES FOR TOOL CALLS:
1. "arguments" MUST be a JSON STRING (not an object)
2. The arguments string MUST use DOUBLE QUOTES for all keys and string values
3. Content with newlines MUST use \\n for line breaks
4. Content with quotes MUST escape them as \\"
5. Do NOT use single quotes in the arguments JSON

EXAMPLES:
CORRECT:
write_file({"path": "hello.py", "content": "print('Hello')"})
write_file({"path": "app.tsx", "content": "import React from 'react';\\n\\nconst App = () => <div>Hello</div>;"})

TOOL-SPECIFIC FORMATS:

1. read_file:
   {"name": "read_file", "arguments": "{\"path\": \"src/file.txt\"}"}

2. write_file:
   {"name": "write_file", "arguments": "{\"path\": \"src/file.txt\", \"content\": \"Your content here with \\\\n for newlines\"}"}

3. replace_edit:
   {"name": "replace_edit", "arguments": "{\"path\": \"src/file.txt\", \"old_str\": \"old text\", \"new_str\": \"new text\"}"}

4. insert_content:
   {"name": "insert_content", "arguments": "{\"path\": \"src/file.txt\", \"content\": \"new content\", \"target\": \"anchor text\", \"position\": \"after\"}"}

5. list_dir:
   {"name": "list_dir", "arguments": "{\"path\": \"src\"}"}

6. run_command:
   {"name": "run_command", "arguments": "{\"command\": \"npm test\"}"}

GUIDELINES FOR MULTI-LINE CONTENT:
When writing code with multiple lines:
- Use \\n for each newline
- Escape any double quotes inside the content as \\"
- For template literals with backticks, use single quotes or escape backticks

Example:
write_file({"path": "store.ts", "content": "import create from \\'zustand\\';\\n\\nexport interface State {\\n  count: number;\\n}\\n\\nconst useStore = create<State>(() => ({\\n  count: 0,\\n}));"})

RESPONSE FORMAT:
- If you need to explain something, provide it in the content field
- Then immediately use the tool call to do the work
- Never output raw code outside of tool calls
- After making changes, verify by reading the file

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
            "name": "replace_edit",
            "description": "Replace an exact string or multi-line block in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "old_str": {"type": "string", "description": "The exact text or multi-line block to replace. Must match exactly."},
                    "new_str": {"type": "string", "description": "The new replacement text or multi-line block."}
                },
                "required": ["path", "old_str", "new_str"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "insert_content",
            "description": "Append before or append after a target string/anchor in a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative path to the file."},
                    "content": {"type": "string", "description": "The text or code to insert."},
                    "target": {"type": "string", "description": "The anchor string to search for. If omitted, appends to EOF or prepends to top of file."},
                    "position": {
                        "type": "string",
                        "enum": ["before", "after"],
                        "description": "Whether to insert 'before' or 'after' the target anchor. Defaults to 'after'."
                    }
                },
                "required": ["path", "content"]
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
    "replace_edit": lambda args: replace_edit(
        args["path"], args["old_str"], args["new_str"]
    ),
    "insert_content": lambda args: insert_content(
        args["path"],
        args["content"],
        target=args.get("target"),
        position=args.get("position", "after"),
    ),
    "edit_file": lambda args: replace_edit(
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
        ui.thinking(iteration + 1, max_iter)

        for attempt in range(5):
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                )
                break
            except RateLimitError as err:
                if attempt == 4:
                    raise
                wait_sec = 2.0 * (attempt + 1)
                ui.warning(f"Rate limit reached (429). Retrying in {wait_sec:.1f}s...")
                time.sleep(wait_sec)

        message = response.choices[0].message

        if not message.tool_calls:
            ui.assistant_response(message.content or "(Task complete)")
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

            ui.tool_call(tool_name, args)
            ui.tool_result(result)

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