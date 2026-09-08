from Agent.tools import read_file, write_file, edit_file, list_dir
from dotenv import load_dotenv
import os
import json
from typing import Callable, Dict, List, Optional

load_dotenv()

_client = None

def _get_client():
    """Lazy client initialization."""
    global _client
    if _client is None:
        from openai import OpenAI
        _client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    return _client


CODING_SYSTEM_PROMPT = """
You are a careful coding agent working inside a project directory.

RULES:
- You have access to tools: read_file, write_file, edit_file, list_dir
- Use these tools to interact with files
- Do NOT generate code in your response - use write_file instead
- For write_file, provide path and content as JSON
- For edit_file, provide path, old_str, and new_str
- For read_file, provide path only
- Once task is over stop tool calling
- Always verify your changes by reading the file after editing
- Think step by step before making changes

TOOL CALL FORMAT:
When using a tool, provide the arguments in valid JSON format.
Example: write_file({"path": "hello.py", "content": "print('Hello')"})

RESPONSE FORMAT:
- If you need to explain something, do it in the content field
- Then use the tool calls to actually do the work
- Never output raw code unless it's inside a tool call
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
                    "path": {"type": "string", "description": "Relative path to the file"}
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
                    "path": {"type": "string", "description": "Relative path to the file"},
                    "content": {"type": "string", "description": "Content to write to the file"}
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
                    "path": {"type": "string", "description": "Relative path to the file"},
                    "old_str": {"type": "string", "description": "String to replace (must be unique)"},
                    "new_str": {"type": "string", "description": "Replacement string"}
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
                    "path": {"type": "string", "description": "Relative path to the directory"}
                }
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
}


def run_agent_loop(
    task: str,
    system_prompt: str,
    max_iter: int = 50,
    on_step: Optional[Callable] = None,
    model: str = "openai/gpt-oss-20b"
):
    """Run the agent loop to complete a task using tool calls."""
    client = _get_client()
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]

    for iteration in range(max_iter):
        print(f"\n💭 THINKING... (iteration {iteration + 1}/{max_iter})")
        
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
        except Exception as e:
            print(f"❌ API Error: {e}")
            return f"Error: API request failed - {e}"

        message = response.choices[0].message

        if not message.tool_calls:
            print("\n✅ Task completed!")
            print(f"\n📝 Response:\n{message.content}")
            return message.content

        # Store assistant message with tool calls
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

        # Execute each tool call
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                result = f"ERROR: Invalid JSON in tool arguments - {e}"
                args = {}
            else:
                print(f"\n🔧 [TOOL] {tool_name}")
                try:
                    result = TOOL_FUNCTIONS[tool_name](args)
                except Exception as exc:
                    result = f"ERROR: {exc}"
                    print(f"   ❌ {result}")
                else:
                    print(f"   ✅ Success")

            if on_step:
                on_step(tool_name, args, result)

            # Trim message history to avoid context overflow
            MAX_HISTORY = 8
            if len(messages) > MAX_HISTORY:
                messages = messages[:2] + messages[-6:]

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": str(result),
            })

    raise RuntimeError(f"Hit max iterations ({max_iter}). Task may be incomplete.")
