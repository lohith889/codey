from tools import read_file, write_file, edit_file, list_dir
from openai import OpenAI
from dotenv import load_dotenv
import os
import json


load_dotenv()

client = OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

CODING_SYSTEM_PROMPT = """
You are a careful coding agent working inside a project directory.

RULES:
- You have access to tools: read_file, write_file, edit_file, list_dir
- use these tools to interact with files
- Do NOT generate code in your response - use write_file instead
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


def run_agent_loop(task: str,system_prompt:str, max_iter: int = 20, on_step=None):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task},
    ]

    for _ in range(max_iter):
        print("THINKING...\n")
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        message = response.choices[0].message

        if not message.tool_calls:
            print("\nAssistant:\n")
            print(message.content)
            return message.content

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
            args = json.loads(tool_call.function.arguments)
            print(f"\n[TOOL] {tool_name}")
            try:
                result = TOOL_FUNCTIONS[tool_name](args)
            except Exception as exc:
                result = f"ERROR: {exc}"

            if on_step:
                on_step(tool_name, args, result)

            MAX_HISTORY = 8
            if len(messages) > MAX_HISTORY:
                messages = messages[:2] + messages[-6:]

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_name,
                "content": str(result),
            })

    raise RuntimeError(f"Hit max iterations ({max_iter})")
