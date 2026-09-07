"""Command line interface for the todo manager.

The CLI provides subcommands: add, list, complete, delete.
"""

import argparse
import sys

from todo_manager import (
    create_todo,
    delete_todo,
    complete_todo,
    list_todos,
)


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(
        prog="todo",
        description="Simple command line todo manager.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Create a new todo")
    add_parser.add_argument("title", help="Title of the todo")
    add_parser.add_argument("-d", "--description", default="", help="Optional description")

    # List subcommand
    subparsers.add_parser("list", help="List all todos")

    # Complete subcommand
    complete_parser = subparsers.add_parser("complete", help="Mark a todo as completed")
    complete_parser.add_argument("id", type=int, help="ID of the todo to complete")

    # Delete subcommand
    delete_parser = subparsers.add_parser("delete", help="Delete a todo")
    delete_parser.add_argument("id", type=int, help="ID of the todo to delete")

    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)

    if args.command == "add":
        todo = create_todo(args.title, args.description)
        print(f"Added todo: {todo}")
    elif args.command == "list":
        todos = list_todos()
        if not todos:
            print("No todos.")
        else:
            for todo in todos:
                status = "\u2713" if todo.get("completed") else "\u2717"
                print(f"{todo.get('id'):>3} [{status}] {todo.get('title')}")
    elif args.command == "complete":
        success = complete_todo(args.id)
        if success:
            print(f"Todo {args.id} marked as completed.")
        else:
            print(f"Todo {args.id} not found.")
    elif args.command == "delete":
        success = delete_todo(args.id)
        if success:
            print(f"Todo {args.id} deleted.")
        else:
            print(f"Todo {args.id} not found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
