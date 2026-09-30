"""PyInstaller entry; no runtime dependency on a user Python installation.
Symbol locations: docs/code-index.md. Calls the same audited CLI as source mode.
"""

from studio.cli import main

if __name__ == "__main__":
    main()
