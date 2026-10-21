# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: command(argv, timeout, output_limit)@L32; read()@L50; container_arguments(input_directory, name)@L69; diagnostics(local_only)@L102; run(project, local_only, scratch)@L160
# variables: IMAGE@L28; DOCKER@L29; environment@L34; environment@L36; selector@L37; process@L45; output@L48; chunk@L53; endpoint@L106; context@L108; context_code@L108; endpoint@L118; config@L125; prefix@L126; code@L127; output@L127; _@L130; found@L130; code@L136; output@L136; _@L139; found@L139; ready@L162; static@L163; name@L166; directory@L169; path@L170; config@L173; prefix@L175; prefix@L177; code@L179; output@L179; marker@L180; line@L181; lines@L181; result@L189
# parameters: argv@L32; output_limit@L32; timeout@L32; input_directory@L69; name@L69; local_only@L102; local_only@L160; project@L160; scratch@L160
# </code-map>

"""Host broker: no uploaded code runs outside a restricted, named container.

Symbol and variable locations: docs/code-index.md. Docker is a defense-in-depth
boundary, not sufficient for hostile multi-tenant SaaS; see docs/security.md.
"""

import asyncio
import contextlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from studio.analysis import inspect_source
from studio.locations import tool_locations
from studio.models import Project

IMAGE = "code-flow-worker:0.2.0"
DOCKER = os.environ.get("STUDIO_DOCKER", shutil.which("docker") or "docker")


async def command(argv: list[str], timeout: int = 180, output_limit: int = 1572864) -> tuple[int, str]:
    """Bound controller subprocess duration and captured output; never invoke a shell."""
    environment = None
    if len(argv) > 2 and argv[0] == DOCKER and "--host" in argv:
        environment = dict(os.environ)
        for selector in (
            "DOCKER_CONTEXT",
            "DOCKER_HOST",
            "DOCKER_TLS",
            "DOCKER_TLS_VERIFY",
            "DOCKER_CERT_PATH",
        ):
            environment.pop(selector, None)
    process = await asyncio.create_subprocess_exec(
        *argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT, env=environment
    )
    output = bytearray()

    async def read() -> None:
        """Consume small chunks and abort oversized output instead of exhausting memory."""
        assert process.stdout
        while chunk := await process.stdout.read(8192):
            output.extend(chunk)
            if len(output) > output_limit:
                raise ValueError("Runner output limit exceeded")
        await process.wait()

    try:
        await asyncio.wait_for(read(), timeout)
    except BaseException:
        with contextlib.suppress(ProcessLookupError):
            process.kill()
        await process.wait()
        raise
    return process.returncode or 0, output.decode(errors="replace")


def container_arguments(input_directory: Path, name: str) -> list[str]:
    """Construct fixed least-privilege flags; no uploaded values can select mounts or images."""
    return [
        DOCKER,
        "run",
        "--rm",
        "--pull=never",
        "--name",
        name,
        "--network=none",
        "--read-only",
        "--cap-drop=ALL",
        "--security-opt=no-new-privileges",
        "--pids-limit=128",
        "--memory=1g",
        "--memory-swap=1g",
        "--cpus=2",
        "--user=65534:65534",
        "--tmpfs=/tmp:rw,exec,nosuid,nodev,size=256m,mode=1777",
        "--mount",
        f"type=bind,source={(input_directory / 'job.json').resolve()},target=/input/job.json,readonly",
        "--env",
        "HOME=/tmp",
        "--env",
        "DOTNET_CLI_HOME=/tmp",
        "--env",
        "AFL_SKIP_CPUFREQ=1",
        "--env",
        "AFL_I_DONT_CARE_ABOUT_MISSING_CRASHES=1",
        IMAGE,
    ]


async def diagnostics(local_only: bool = False) -> dict:
    """Distinguish missing engine from missing worker image without running target code."""
    try:
        if local_only:
            endpoint = os.environ.get("DOCKER_HOST", "") if not os.environ.get("DOCKER_CONTEXT") else ""
            if not endpoint:
                context_code, context = await command(
                    [DOCKER, "context", "inspect", "--format", "{{json .Endpoints.docker.Host}}"],
                    timeout=8,
                    output_limit=4096,
                )
                if context_code:
                    return {
                        "ready": False,
                        "reason": "Local Docker context is unavailable; no source was transmitted",
                    }
                endpoint = json.loads(context.strip())
            if not isinstance(endpoint, str) or not endpoint.startswith(("unix:///", "npipe:////./pipe/")):
                return {
                    "ready": False,
                    "reason": "Account mode requires a local Unix/named-pipe Docker engine; remote contexts are blocked",
                }
        if local_only:
            with tempfile.TemporaryDirectory(prefix="code-flow-docker-config-") as config:
                prefix = [DOCKER, "--host", endpoint, "--config", config]
                code, output = await command(
                    prefix + ["info", "--format", "{{.ServerVersion}}"], timeout=8, output_limit=16384
                )
                found, _ = (
                    await command(prefix + ["image", "inspect", IMAGE], timeout=8, output_limit=32768)
                    if not code
                    else (1, "")
                )
        else:
            code, output = await command(
                [DOCKER, "info", "--format", "{{.ServerVersion}}"], timeout=8, output_limit=16384
            )
            found, _ = (
                await command([DOCKER, "image", "inspect", IMAGE], timeout=8, output_limit=32768)
                if not code
                else (1, "")
            )
        if code:
            return {
                "ready": False,
                "reason": "Docker engine unavailable; start Docker Desktop or configure an isolated Linux worker",
            }
        return {
            "ready": found == 0,
            "engine": output.strip(),
            "image": IMAGE,
            "reason": "Worker image needs installation" if found else "Ready",
            **({"endpoint": endpoint} if local_only else {}),
        }
    except (OSError, TimeoutError, ValueError):
        return {"ready": False, "reason": "Docker is missing or unresponsive; host execution is disabled"}


async def run(project: Project, local_only: bool = False, scratch: Path | None = None) -> dict:
    """Isolate one immutable project and retain bounded evidence even on failure."""
    ready = await diagnostics(local_only=True) if local_only else await diagnostics()
    static = inspect_source(project)
    if not ready["ready"]:
        return {"tool_status": "blocked", "reason": ready["reason"], "static": static}
    name = "code-flow-" + uuid4().hex
    if scratch is not None:
        scratch.mkdir(parents=True, exist_ok=True, mode=0o700)
    with tempfile.TemporaryDirectory(prefix="code-flow-", dir=scratch) as directory:
        path = Path(directory)
        (path / "job.json").write_text(project.model_dump_json(), encoding="utf-8")
        if local_only:
            config = path / "docker-config"
            config.mkdir()
            prefix = [DOCKER, "--host", ready["endpoint"], "--config", str(config)]
        else:
            prefix = [DOCKER]
        try:
            code, output = await command(prefix + container_arguments(path, name)[1:])
            marker = "STUDIO_RESULT="
            lines = [line[len(marker) :] for line in output.splitlines() if line.startswith(marker)]
            if code or len(lines) != 1:
                return {
                    "tool_status": "runner-error",
                    "reason": "Worker did not produce one valid result",
                    "log": output[-8192:],
                    "static": static,
                }
            result = json.loads(lines[0])
            if not isinstance(result, dict) or "tool_status" not in result:
                raise ValueError("Malformed worker evidence")
            return {
                **result,
                **tool_locations(result, project),
                "static": static,
                "isolation": {
                    "network": "none",
                    "memory_mib": 1024,
                    "cpus": 2,
                    "pids": 128,
                    "read_only": True,
                },
            }
        except (OSError, TimeoutError, ValueError) as error:
            return {"tool_status": "runner-error", "reason": type(error).__name__, "static": static}
        finally:
            # Kill only this broker-owned exact container, never unrelated jobs.
            with contextlib.suppress(OSError, TimeoutError, ValueError):
                await command(prefix + ["rm", "--force", name], timeout=10, output_limit=4096)
