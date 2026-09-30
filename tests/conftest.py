# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: project()@L17
# </code-map>

"""Trusted app test fixtures; never execute arbitrary uploaded programs on the host.
Symbol and variable locations: docs/code-index.md.
"""

import pytest

from studio.models import Project


@pytest.fixture
def project():
    """A minimal validated manifest used as inert controller input."""
    return Project(
        title="Counter",
        language="python",
        entry="main.py",
        files=[{"name": "main.py", "content": "print(4)\n"}],
        cases=[{"name": "four", "stdin": "", "stdout": "4"}],
    )
