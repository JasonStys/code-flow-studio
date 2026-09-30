# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: command(argv, timeout, output_limit)@L31; read()@L38; container_arguments(input_directory, name)@L57; diagnostics()@L90; run(project)@L112
# variables: IMAGE@L27; DOCKER@L28; process@L33; output@L36; chunk@L41; code@L93; output@L93; _@L101; found@L101; ready@L114; static@L115; name@L118; directory@L119; path@L120; code@L123; output@L123; prefix@L124; line@L125; lines@L125; result@L133
# parameters: argv@L31; output_limit@L31; timeout@L31; input_directory@L57; name@L57; project@L112
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
from studio.models import Project

IMAGE = "code-flow-worker:0.1.0"
DOCKER = os.environ.get("STUDIO_DOCKER", shutil.which("docker") or "docker")


async def command(argv: list[str], timeout: int = 180, output_limit: int = 1572864) -> tuple[int, str]:
    """Bound controller subprocess duration and captured output; never invoke a shell."""
    process = await asyncio.create_subprocess_exec(
        *argv, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
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


async def diagnostics() -> dict:
    """Distinguish missing engine from missing worker image without running target code."""
    try:
        code, output = await command(
            [DOCKER, "info", "--format", "{{.ServerVersion}}"], timeout=8, output_limit=16384
        )
        if code:
            return {
                "ready": False,
                "reason": "Docker engine unavailable; start Docker Desktop or configure an isolated Linux worker",
            }
        found, _ = await command([DOCKER, "image", "inspect", IMAGE], timeout=8, output_limit=32768)
        return {
            "ready": found == 0,
            "engine": output.strip(),
            "image": IMAGE,
            "reason": "Worker image needs installation" if found else "Ready",
        }
    except (OSError, TimeoutError, ValueError):
        return {"ready": False, "reason": "Docker is missing or unresponsive; host execution is disabled"}


async def run(project: Project) -> dict:
    """Isolate one immutable project and retain bounded evidence even on failure."""
    ready = await diagnostics()
    static = inspect_source(project)
    if not ready["ready"]:
        return {"tool_status": "blocked", "reason": ready["reason"], "static": static}
    name = "code-flow-" + uuid4().hex
    with tempfile.TemporaryDirectory(prefix="code-flow-") as directory:
        path = Path(directory)
        (path / "job.json").write_text(project.model_dump_json(), encoding="utf-8")
        try:
            code, output = await command(container_arguments(path, name))
            prefix = "STUDIO_RESULT="
            lines = [line[len(prefix) :] for line in output.splitlines() if line.startswith(prefix)]
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
                await command([DOCKER, "rm", "--force", name], timeout=10, output_limit=4096)
