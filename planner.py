import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client=OpenAI(
    api_key=os.getenv("API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

PLANNER_SYSTEM_PROMPT = """
You turn a coding task into a short numbered plan.
Breakdown the huge task into multiple units so acheiving the goal is efficient.
Keep it to the smallest set of steps that accomplishes the task.
Give proper condition to end the task so the agent stops tool calling repeatedly

"""
steps_schema = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "description": "List of steps to accomplish the task",
            "items": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Step number/identifier",
                        "minimum": 1
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of what this step does"
                    },
                    "files_touched": {
                        "type": "array",
                        "description": "List of files that will be modified/created",
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["id", "description","files_touched"],
                "additionalProperties": False
            }
        }
    },
    "required": ["steps"],
    "additionalProperties": False
}

def generate_plan(task: str) -> dict:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ],
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema":
              {
                "name": "task_steps",
                "description": "A structured plan of steps to accomplish a task",
                "schema": steps_schema,
                "strict": True
              }
          }

    )
    
    raw = response.choices[0].message.content
    return json.loads(raw)
