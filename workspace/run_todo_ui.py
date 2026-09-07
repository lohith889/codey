"""Single runnable script that starts the Todo Manager UI.

This script imports the UI module and runs the Tkinter event loop.  The
``todo_manager`` module is imported by ``ui.py`` itself, so all logic for
creating, listing, completing, and deleting todos is already available.

To execute the application simply run:

```bash
python run_todo_ui.py
```
"""

from ui import main

if __name__ == "__main__":
    main()
