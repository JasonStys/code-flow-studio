# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: native_stage(stage, connections, tasks)@L18
# variables: counts@L21; count@L26; name@L26
# parameters: connections@L18; stage@L18; tasks@L18
# </code-map>

"""Jason Stys: opt-in native-test lifecycle milestones containing no account or source values.

Symbol locations: docs/code-index.md. This logger never records request bodies or paths.
"""

import json
import os


def native_stage(stage: str, *, connections: int | None = None, tasks: int | None = None) -> None:
    """Expose a fixed caller-supplied milestone and owned process identities only in native test mode."""
    if os.environ.get("STUDIO_DESKTOP_TEST") == "1":
        counts = {"connections": connections, "tasks": tasks}
        print(
            "NATIVE_SERVICE_STAGE",
            json.dumps({
                "stage": stage, "pid": os.getpid(), "parent_pid": os.getppid(),
                **{name: count for name, count in counts.items() if type(count) is int and count >= 0},
            }),
            flush=True,
        )
