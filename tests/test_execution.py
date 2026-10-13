# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_fixed_container_flags(tmp_path)@L19; test_command_limit()@L28; test_command_timeout()@L34; test_no_host_fallback(project, monkeypatch)@L40; unavailable()@L43; test_private_remote_context_blocked(endpoint, monkeypatch)@L54; forbidden()@L59; test_private_local_context_and_scoped_job(project, monkeypatch, tmp_path)@L66; fake_command(argv)@L71; test_context_overrides_host_but_remote_source_stays_blocked(monkeypatch)@L93; context_only(argv)@L98
# variables: args@L21; value@L24; value@L25; result@L47; observed@L69; argv@L75; mount@L80; x@L80; result@L87; argv@L89
# parameters: tmp_path@L19; monkeypatch@L40; project@L40; endpoint@L54; monkeypatch@L54; args@L59; kwargs@L59; monkeypatch@L66; project@L66; tmp_path@L66; argv@L71; kwargs@L71; monkeypatch@L93; argv@L98; kwargs@L98
# </code-map>

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


@pytest.mark.parametrize(
    "endpoint", ["ssh://remote.example", "tcp://127.0.0.1:2375", "https://remote.example"]
)
def test_private_remote_context_blocked(endpoint, monkeypatch):
    """Reject remote engines before an info/image/run command can transmit source."""
    monkeypatch.setenv("DOCKER_HOST", endpoint)
    monkeypatch.delenv("DOCKER_CONTEXT", raising=False)

    async def forbidden(*args, **kwargs):
        raise AssertionError("Remote engine must not be contacted")

    monkeypatch.setattr(execution, "command", forbidden)
    assert not asyncio.run(execution.diagnostics(local_only=True))["ready"]


def test_private_local_context_and_scoped_job(project, monkeypatch, tmp_path):
    """Synthetic protocol test checks local context, secret-free mounts and cleanup, not actual compiler correctness."""
    monkeypatch.delenv("DOCKER_HOST", raising=False)
    observed = []

    async def fake_command(argv, **kwargs):
        if argv[1] == "--host":
            assert argv[2] == "unix:///var/run/docker.sock"
            assert argv[3] == "--config"
            argv = [argv[0]] + argv[5:]
        observed.append(argv)
        if argv[1:3] == ["context", "inspect"]:
            return 0, '"unix:///var/run/docker.sock"'
        if argv[1] == "run":
            mount = next(x for x in argv if x.startswith("type=bind"))
            assert str(tmp_path.resolve()) in mount
            assert "providers.private.json" not in " ".join(argv)
            return 0, 'STUDIO_RESULT={"tool_status":"completed","checks":{"passed":1,"failed":0}}'
        return 0, "fixture"

    monkeypatch.setattr(execution, "command", fake_command)
    result = asyncio.run(execution.run(project, local_only=True, scratch=tmp_path / "jobs"))
    assert result["tool_status"] == "completed" and result["isolation"]["network"] == "none"
    assert any(argv[1:3] == ["rm", "--force"] for argv in observed)
    assert not list((tmp_path / "jobs").iterdir())


def test_context_overrides_host_but_remote_source_stays_blocked(monkeypatch):
    """Docker's DOCKER_CONTEXT precedence cannot bypass a local-host declaration."""
    monkeypatch.setenv("DOCKER_HOST", "unix:///var/run/docker.sock")
    monkeypatch.setenv("DOCKER_CONTEXT", "fictional-remote")

    async def context_only(argv, **kwargs):
        assert argv[1:3] == ["context", "inspect"]
        return 0, '"ssh://remote.example"'

    monkeypatch.setattr(execution, "command", context_only)
    assert not asyncio.run(execution.diagnostics(local_only=True))["ready"]
