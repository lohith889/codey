"""Simple todo manager with CRUD operations stored in a local JSON file.

The module provides a lightweight interface for creating, listing, completing, and
deleting todos.  All data is persisted to `todos.json` in the same directory.
"""

import json
import os
from typing import List, Dict, Any

# Path to the JSON file that stores the todos.
_FILE_PATH = os.path.join(os.path.dirname(__file__), "todos.json")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_todos() -> List[Dict[str, Any]]:
    """Load the list of todos from the JSON file.

    If the file does not exist or is empty, an empty list is returned.
    """
    if not os.path.exists(_FILE_PATH):
        return []
    try:
        with open(_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
    except json.JSONDecodeError:
        # Corrupted file – start fresh
        return []
    return []


def _save_todos(todos: List[Dict[str, Any]]) -> None:
    """Persist the list of todos to the JSON file."""
    with open(_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(todos, f, indent=4, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_todo(title: str, description: str = "") -> Dict[str, Any]:
    """Create a new todo item.

    Parameters
    ----------
    title:
        The title of the todo.
    description:
        Optional description.

    Returns
    -------
    dict
        The created todo object.
    """
    todos = _load_todos()
    new_id = 1
    if todos:
        # Find the maximum existing ID and increment.
        new_id = max(todo.get("id", 0) for todo in todos) + 1
    todo = {
        "id": new_id,
        "title": title,
        "description": description,
        "completed": False,
    }
    todos.append(todo)
    _save_todos(todos)
    return todo


def list_todos() -> List[Dict[str, Any]]:
    """Return a list of all todo items."""
    return _load_todos()


def complete_todo(todo_id: int) -> bool:
    """Mark a todo as completed.

    Returns ``True`` if the todo was found and updated, otherwise ``False``.
    """
    todos = _load_todos()
    for todo in todos:
        if todo.get("id") == todo_id:
            todo["completed"] = True
            _save_todos(todos)
            return True
    return False


def delete_todo(todo_id: int) -> bool:
    """Delete a todo by its ID.

    Returns ``True`` if a todo was removed, otherwise ``False``.
    """
    todos = _load_todos()
    new_todos = [t for t in todos if t.get("id") != todo_id]
    if len(new_todos) == len(todos):
        # No todo matched the ID
        return False
    _save_todos(new_todos)
    return True

# End of module
