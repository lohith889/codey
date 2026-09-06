import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client=OpenAI(
    api_key=os.env("API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

PLANNER_SYSTEM_PROMPT = """
You turn a coding task into a short numbered plan.

Output ONLY valid JSON, no prose, in this exact shape:

{
  "steps": [
    {
      "id": 1,
      "description": "...",
      "files_touched": ["path/to/file.py"]
    }
  ]
}

Keep it to the smallest set of steps that accomplishes the task.
"""
def generate_plan(task: str) -> dict:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ],
        temperature=0,
        response_format={"type": "json_object"}
    )

    raw = response.choices[0].message.content
    return json.loads(raw)