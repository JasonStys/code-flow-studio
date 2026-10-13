# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# </code-map>

"""PyInstaller entry; no runtime dependency on a user Python installation.
Symbol locations: docs/code-index.md. Calls the same audited CLI as source mode.
"""

from multiprocessing import freeze_support

from studio.private_cli import main

if __name__ == "__main__":
    freeze_support()
    main()
