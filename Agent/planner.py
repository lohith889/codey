import json
import os
from dotenv import load_dotenv
from agent_core import get_client
import ui

load_dotenv()

PLANNER_SYSTEM_PROMPT = """
You turn a coding task into a short numbered plan.
Breakdown the huge task into multiple units so achieving the goal is efficient.
Keep it to the smallest set of steps that accomplishes the task.
Give proper conditions to end the task so the agent stops tool calling repeatedly.
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

def generate_plan(task: str, max_retries: int = 3) -> dict:
    client = get_client()
    model = os.getenv("PLANNER_MODEL_NAME") or os.getenv("MODEL_NAME", "openai/gpt-oss-20b")

    messages = [
        {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
        {"role": "user", "content": task},
    ]

    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "task_steps",
                        "description": "A structured plan of steps to accomplish a task",
                        "schema": steps_schema,
                        "strict": True,
                    },
                },
            )

            raw = response.choices[0].message.content
            if not raw:
                raise ValueError("Planner returned an empty response.")

            plan = json.loads(raw)
            if not isinstance(plan, dict) or "steps" not in plan or not plan["steps"]:
                raise ValueError("Planner returned a plan missing the 'steps' list.")

            return plan

        except Exception as exc:
            last_error = exc
            ui.warning(f"Plan generation attempt {attempt}/{max_retries} failed: {exc}")
            if attempt < max_retries:
                messages.append({
                    "role": "user",
                    "content": f"The previous plan generation attempt failed: {exc}. Please generate a valid JSON plan strictly conforming to the schema.",
                })

    raise RuntimeError(
        f"Planner failed to generate a valid plan after {max_retries} attempts. Last error: {last_error}"
    )

