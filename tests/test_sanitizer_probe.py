# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_probe_retains_every_existing_container_boundary_and_exact_owned_cleanup(monkeypatch)@L23; command(argv)@L27; test_missing_or_failed_probe_is_not_accepted(monkeypatch, code, output)@L58; command(argv)@L61
# variables: observed@L25; required@L31; item@L45; item@L46; result@L51; name@L53
# parameters: monkeypatch@L23; argv@L27; kwargs@L27; code@L58; monkeypatch@L58; output@L58; argv@L61; kwargs@L61
# </code-map>

"""Test the trusted CI probe's unchanged container restrictions without running targets on the host.

Jason Stys: protocol/cleanup tests only; actual ASan startup/fault detection runs in CI containers.
Exact definition and variable locations are generated in docs/code-index.md.
"""

import asyncio
import json

import pytest

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
