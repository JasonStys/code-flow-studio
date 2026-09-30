# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: main()@L26
# variables: output@L28; manifest@L30; project@L31; evidence@L32; config@L39; config_json@L40; router@L41; directory@L44; path@L45; router@L47; router@L49; tests@L51; payload@L52; tested@L54; generated@L55; improved@L56; replacements@L57; item@L59; row@L59; candidate@L61
# </code-map>

"""Push-triggered generation, test validation and candidate evaluation.

Symbol and variable locations: docs/code-index.md. API access is optional and
push-only. No credential ever enters the compiler container; no code is committed.
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path

from examples.projects import fixture
from studio.execution import run
from studio.models import AIRequest, Project
from studio.providers import Providers


async def main():
    """Always test a synthetic baseline; if configured, generate tests and an improved candidate."""
    output = Path("artifacts/push-analysis")
    output.mkdir(parents=True, exist_ok=True)
    manifest = Path("code-flow.project.json")
    project = Project.model_validate_json(manifest.read_text()) if manifest.exists() else fixture("python")
    evidence = {
        "baseline": await run(project),
        "ai": {
            "status": "not-configured",
            "reason": "Set a private provider configuration and credentials to enable generation",
        },
    }
    config = os.environ.get("STUDIO_PROVIDER_CONFIG")
    config_json = os.environ.get("STUDIO_AI_CONFIG")
    router = None
    if config_json:
        # Private CI configuration never enters repository artifacts or compiler mounts.
        with tempfile.TemporaryDirectory(prefix="code-flow-provider-") as directory:
            path = Path(directory) / "providers.json"
            path.write_text(config_json, encoding="utf-8")
            router = Providers(path)
    elif config:
        router = Providers(Path(config))
    if router:
        tests = await router.request(AIRequest(task="tests", project=project, consent=True))
        payload = project.model_dump()
        payload["tests"] += "\n" + tests["proposal"]["tests"]
        tested = Project.model_validate(payload)
        generated = await run(tested)
        improved = await router.request(AIRequest(task="improve", project=tested, consent=True))
        replacements = improved["proposal"]["files"]
        payload["files"] = [
            row for row in payload["files"] if row["name"] not in {item["name"] for item in replacements}
        ] + replacements
        candidate = Project.model_validate(payload)
        evidence["ai"] = {
            "status": "generated",
            "tests_proposal": tests,
            "improvement_proposal": improved,
            "generated_tests_run": generated,
            "candidate_run": await run(candidate),
            "promotion": "Developer review required; source is never automatically committed",
        }
        (output / "candidate.project.json").write_text(candidate.model_dump_json(indent=2))
        (output / "test_generated.py").write_text(tested.tests)
    (output / "history.json").write_text(json.dumps(evidence, indent=2))
    if evidence["baseline"]["tool_status"] != "completed" or evidence["baseline"].get("checks", {}).get(
        "failed"
    ):
        raise SystemExit("Baseline failed; inspect retained evidence")


if __name__ == "__main__":
    asyncio.run(main())
