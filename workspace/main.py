"""Entry point for the todo command-line tool.

This module simply imports and runs the :func:`cli.main` function.
"""

import sys

from cli import main

if __name__ == "__main__":
    sys.exit(main())
