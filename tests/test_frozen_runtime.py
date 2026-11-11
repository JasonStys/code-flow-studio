# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_unreviewed_frozen_runtime_refuses_before_service_import(monkeypatch, version)@L24; test_reviewed_frozen_and_supported_source_dispatch(monkeypatch, frozen, version)@L39
# variables: events@L26; service@L30; events@L41; service@L45
# parameters: monkeypatch@L24; version@L24; frozen@L39; monkeypatch@L39; version@L39
# </code-map>

"""Jason Stys: refuse an unreviewed frozen interpreter before account-service imports.

The synthetic module records dispatch without opening accounts or running a server.
Definition and variable locations are generated in the repository code index.
"""

import runpy
import sys
import types
from pathlib import Path

import pytest


@pytest.mark.parametrize("version", [(3, 12, 10), (3, 14, 6), (3, 14, 11)])
def test_unreviewed_frozen_runtime_refuses_before_service_import(monkeypatch, version):
    """A stale or unexpected frozen SDK must not reach private account setup."""
    events = []
    monkeypatch.setattr("multiprocessing.freeze_support", lambda: events.append("freeze"))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "version_info", version)
    service = types.ModuleType("studio.private_cli")
    service.main = lambda: events.append("service")
    monkeypatch.setitem(sys.modules, "studio.private_cli", service)
    with pytest.raises(SystemExit, match="reviewed Python 3.14.10"):
        runpy.run_path(str(Path(__file__).parents[1] / "scripts/frozen_entry.py"), run_name="__main__")
    assert events == ["freeze"]


@pytest.mark.parametrize("frozen,version", [(True, (3, 14, 10)), (False, (3, 12, 10))])
def test_reviewed_frozen_and_supported_source_dispatch(monkeypatch, frozen, version):
    """The reviewed binary and source-development modes retain their normal CLI."""
    events = []
    monkeypatch.setattr("multiprocessing.freeze_support", lambda: events.append("freeze"))
    monkeypatch.setattr(sys, "frozen", frozen, raising=False)
    monkeypatch.setattr(sys, "version_info", version)
    service = types.ModuleType("studio.private_cli")
    service.main = lambda: events.append("service")
    monkeypatch.setitem(sys.modules, "studio.private_cli", service)
    runpy.run_path(str(Path(__file__).parents[1] / "scripts/frozen_entry.py"), run_name="__main__")
    assert events == ["freeze", "service"]
