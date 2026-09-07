"""Simple Tkinter UI for the todo manager.

This UI provides a basic graphical interface to list, create, complete, and
delete todo items using the :mod:`todo_manager` module.
"""

import tkinter as tk
from tkinter import simpledialog, messagebox

# Import the todo manager functions
from todo_manager import (
    create_todo,
    list_todos,
    complete_todo,
    delete_todo,
)


def main() -> None:
    """Start the Tkinter event loop."""
    root = tk.Tk()
    root.title("Todo Manager UI")

    # Listbox to display todos
    listbox = tk.Listbox(root, width=50, height=15)
    listbox.pack(padx=10, pady=10)

    # Store mapping of list index -> todo id
    todo_id_map = []  # type: list[int]

    def refresh_list() -> None:
        """Refresh the listbox from the current data."""
        listbox.delete(0, tk.END)
        todo_id_map.clear()
        for todo in list_todos():
            status = "[x]" if todo.get("completed") else "[ ]"
            title = todo.get("title", "")
            listbox.insert(tk.END, f"{status} {title}")
            todo_id_map.append(todo.get("id"))

    def add_todo() -> None:
        title = simpledialog.askstring("Add Todo", "Title:")
        if not title:
            return
        description = simpledialog.askstring("Add Todo", "Description:") or ""
        create_todo(title, description)
        refresh_list()

    def complete_selected() -> None:
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Complete Todo", "No todo selected.")
            return
        idx = selection[0]
        todo_id = todo_id_map[idx]
        if complete_todo(todo_id):
            refresh_list()
        else:
            messagebox.showerror("Error", "Failed to complete todo.")

    def delete_selected() -> None:
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Delete Todo", "No todo selected.")
            return
        idx = selection[0]
        todo_id = todo_id_map[idx]
        if delete_todo(todo_id):
            refresh_list()
        else:
            messagebox.showerror("Error", "Failed to delete todo.")

    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="Add", width=10, command=add_todo).grid(
        row=0, column=0, padx=5
    )
    tk.Button(btn_frame, text="Complete", width=10, command=complete_selected).grid(
        row=0, column=1, padx=5
    )
    tk.Button(btn_frame, text="Delete", width=10, command=delete_selected).grid(
        row=0, column=2, padx=5
    )

    refresh_list()
    root.mainloop()


if __name__ == "__main__":
    main()
