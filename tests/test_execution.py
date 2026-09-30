"""Container boundary and bounded subprocess tests. Symbols: docs/code-index.md."""

import asyncio
import sys

import pytest

from studio import execution


def test_fixed_container_flags(tmp_path):
    """No host secrets, network, Docker socket or broad host mounts enter a worker."""
    args = execution.container_arguments(tmp_path, "code-flow-owned")
    assert "--network=none" in args and "--read-only" in args and "--cap-drop=ALL" in args
    assert "--pids-limit=128" in args and "--memory=1g" in args
    assert len([value for value in args if value.startswith("type=bind")]) == 1
    assert all("docker.sock" not in value and "API_KEY" not in value for value in args)


def test_command_limit():
    """Controller subprocess output is bounded independently of target behavior."""
    with pytest.raises(ValueError, match="limit"):
        asyncio.run(execution.command([sys.executable, "-c", "print('x' * 10000)"], output_limit=100))


def test_command_timeout():
    """Even diagnostic subprocesses cannot hang the UI indefinitely."""
    with pytest.raises(TimeoutError):
        asyncio.run(execution.command([sys.executable, "-c", "import time; time.sleep(2)"], timeout=0.1))


def test_no_host_fallback(project, monkeypatch):
    """Unavailable isolation leaves source unexecuted and the outcome explicitly blocked."""

    async def unavailable():
        return {"ready": False, "reason": "Missing Docker"}

    monkeypatch.setattr(execution, "diagnostics", unavailable)
    result = asyncio.run(execution.run(project))
    assert result["tool_status"] == "blocked" and "checks" not in result
