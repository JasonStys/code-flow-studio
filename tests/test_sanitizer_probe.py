# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_probe_retains_every_existing_container_boundary_and_exact_owned_cleanup(monkeypatch)@L24; command(argv)@L28; test_missing_or_failed_probe_is_not_accepted(monkeypatch, code, output)@L59; command(argv)@L62; test_optional_metadata_never_requires_elevating_container_permissions(monkeypatch, tmp_path, failure)@L71; denied()@L74; test_readable_metadata_is_retained(tmp_path)@L82
# variables: observed@L26; required@L32; item@L46; item@L47; result@L52; name@L54; file@L84
# parameters: monkeypatch@L24; argv@L28; kwargs@L28; code@L59; monkeypatch@L59; output@L59; argv@L62; kwargs@L62; failure@L71; monkeypatch@L71; tmp_path@L71; args@L74; kwargs@L74; tmp_path@L82
# </code-map>

"""Test the trusted CI probe's unchanged container restrictions without running targets on the host.

Jason Stys: protocol/cleanup tests only; actual ASan startup/fault detection runs in CI containers.
Exact definition and variable locations are generated in docs/code-index.md.
"""

import asyncio
import json

import pytest

from runner.sanitizer_probe import optional_metadata
from scripts import worker_checks


def test_probe_retains_every_existing_container_boundary_and_exact_owned_cleanup(monkeypatch):
    """The diagnostic entry point must not gain network, writable root, privileges or host data."""
    observed = []

    async def command(argv, **kwargs):
        """Supply only a synthetic protocol response; no process or compiler is executed."""
        observed.append(argv)
        if "run" in argv:
            for required in [
                "--network=none",
                "--read-only",
                "--cap-drop=ALL",
                "--security-opt=no-new-privileges",
                "--pids-limit=128",
                "--memory=1g",
                "--memory-swap=1g",
                "--cpus=2",
                "--user=65534:65534",
            ]:
                assert required in argv
            assert argv[-1] == "/opt/sanitizer_probe.py"
            assert "--entrypoint=python" in argv
            assert len([item for item in argv if item.startswith("type=bind")]) == 1
            assert not any("privileged" in item or "seccomp=unconfined" in item for item in argv)
            return 0, "SANITIZER_PROBE=" + json.dumps({"status": "passed", "candidate": {"failures": 0}})
        return 0, ""

    monkeypatch.setattr(worker_checks, "command", command)
    result = asyncio.run(worker_checks.sanitizer_startup_checks())
    assert result["status"] == "passed"
    name = observed[0][observed[0].index("--name") + 1]
    assert observed[-1] == [worker_checks.DOCKER, "rm", "--force", name]


@pytest.mark.parametrize("code,output", [(1, 'SANITIZER_PROBE={"status":"failed"}'), (0, "no marker")])
def test_missing_or_failed_probe_is_not_accepted(monkeypatch, code, output):
    """A diagnostic failure stays failed; old startup failures cannot erase candidate findings."""

    async def command(argv, **kwargs):
        """Simulate a failed/invalid owned probe and successful cleanup only."""
        return (code, output) if "run" in argv else (0, "")

    monkeypatch.setattr(worker_checks, "command", command)
    assert asyncio.run(worker_checks.sanitizer_startup_checks())["status"] == "failed"


@pytest.mark.parametrize("failure", [PermissionError, FileNotFoundError])
def test_optional_metadata_never_requires_elevating_container_permissions(monkeypatch, tmp_path, failure):
    """Only environmental metadata may be unavailable; compiler/fault controls remain required."""

    def denied(*args, **kwargs):
        """Model a masked proc or absent cgroup path without touching system permissions."""
        raise failure("synthetic unavailable metadata")

    monkeypatch.setattr(type(tmp_path), "read_text", denied)
    assert optional_metadata(tmp_path / "metadata") == "unavailable (" + failure.__name__ + ")"


def test_readable_metadata_is_retained(tmp_path):
    """Normal environment values remain observable without special privileges."""
    file = tmp_path / "metadata"
    file.write_text("32\n", encoding="utf-8")
    assert optional_metadata(file) == "32"
