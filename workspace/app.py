"""Combined application entry point.

This single script imports the UI module and starts the Tkinter event loop.
It relies on the :mod:`todo_manager` module for data persistence.

Running ``python app.py`` will launch the GUI.
"""

from ui import main as ui_main

if __name__ == "__main__":
    ui_main()
