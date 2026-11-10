# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: native_stage(stage)@L17
# parameters: stage@L17
# </code-map>

"""Jason Stys: opt-in native-test lifecycle milestones containing no account or source values.

Symbol locations: docs/code-index.md. This logger never records request bodies or paths.
"""

import json
import os


def native_stage(stage: str) -> None:
    """Expose a fixed caller-supplied milestone and owned process identities only in native test mode."""
    if os.environ.get("STUDIO_DESKTOP_TEST") == "1":
        print(
            "NATIVE_SERVICE_STAGE",
            json.dumps({"stage": stage, "pid": os.getpid(), "parent_pid": os.getppid()}),
            flush=True,
        )
