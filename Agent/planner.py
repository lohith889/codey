import json
import os
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None

def _get_client():
    """Lazy client initialization."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("API_KEY"),
            base_url="https://api.groq.com/openai/v1"
        )
    return _client


PLANNER_SYSTEM_PROMPT = """
You turn a coding task into a short numbered plan.
Break down the huge task into multiple units so achieving the goal is efficient.
Keep it to the smallest set of steps that accomplishes the task.
Give proper conditions to end the task so the agent stops tool calling repeatedly.

Focus on:
1. Understanding the task requirements
2. Identifying files that need to be created or modified
3. Breaking down into logical, sequential steps
4. Defining clear completion criteria
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
                "required": ["id", "description", "files_touched"],
                "additionalProperties": False
            }
        },
        "completion_criteria": {
            "type": "string",
            "description": "Clear conditions that indicate the task is complete"
        }
    },
    "required": ["steps", "completion_criteria"],
    "additionalProperties": False
}


def generate_plan(task: str) -> Dict:
    """Generate a structured plan for completing a coding task."""
    client = _get_client()
    print("📋 Generating plan...")
    
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
            {"role": "user", "content": task},
        ],
        temperature=0.3,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "task_steps",
                "description": "A structured plan of steps to accomplish a task",
                "schema": steps_schema,
                "strict": True
            }
        }
    )
    
    raw = response.choices[0].message.content
    plan = json.loads(raw)
    
    print(f"✅ Plan generated with {len(plan['steps'])} steps")
    return plan
