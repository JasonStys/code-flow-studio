# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# </code-map>

"""PyInstaller entry; no runtime dependency on a user Python installation.
Symbol locations: docs/code-index.md. Calls the same audited CLI as source mode.
"""

import sys
from multiprocessing import freeze_support

if __name__ == "__main__":
    freeze_support()
    if getattr(sys, "frozen", False) and sys.version_info[:3] != (3, 14, 10):
        raise SystemExit("This application requires its reviewed Python 3.14.10 runtime.")
    from studio.private_cli import main

    main()
