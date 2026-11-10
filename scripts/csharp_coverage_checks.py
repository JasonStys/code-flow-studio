# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: exit_project()@L39; collector_fault(mode)@L62; validate_collector_fault(record)@L137; checks(record, output)@L172; save()@L175; main()@L244
# variables: PROGRAM@L29; code@L48; expected@L48; name@L48; value@L48; project@L65; program@L76; name@L107; directory@L108; root@L109; argv@L111; argv@L113; output@L115; status@L115; results@L117; line@L119; observations@L122; line@L124; observed@L128; result@L128; mode@L139; observed@L139; result@L139; temporary@L177; project@L181; result@L182; case@L188; changed@L192; unexpected@L194; case@L203; fault@L222; mode@L236; parser@L246; args@L249; root@L250; identity@L251; bridge@L252; record@L253; output@L260
# parameters: mode@L62; record@L137; output@L172; record@L172
# </code-map>

"""Jason Stys: hosted-only actual .NET/Coverlet exit and collector-failure acceptance.

Healthy target rejection is distinct from a failed collector. Local tests may
inspect inert manifests; main refuses compiler/container execution on this PC.
"""

import argparse
import asyncio
import contextlib
import hashlib
import json
import tempfile
from pathlib import Path
from uuid import uuid4

import studio
from scripts.compiler_acceptance import provenance, require, validate_positive
from studio import execution
from studio.models import Project

PROGRAM = """// Return an explicitly requested CLI status; malformed input is an approved rejection.
using System.Globalization;
string text = Console.In.ReadToEnd().Trim();
int code = int.TryParse(text, NumberStyles.None, CultureInfo.InvariantCulture, out int parsed)
    && parsed <= 255 ? parsed : 2;
Console.WriteLine($"exit={code}");
return code;
"""


def exit_project() -> Project:
    """Independent literal oracles cover ordinary success and distinct approved nonzero returns."""
    return Project(
        title="C# exact instrumented exit contract",
        language="csharp",
        entry="Program.cs",
        files=[{"name": "Program.cs", "content": PROGRAM}],
        cases=[
            {"name": name, "stdin": value, "stdout": expected, "exit_code": code}
            for name, value, expected, code in [
                ("success-zero", "0\n", "exit=0", 0),
                ("expected-one", "1\n", "exit=1", 1),
                ("expected-two", "2\n", "exit=2", 2),
                ("expected-seven", "7\n", "exit=7", 7),
                ("expected-255", "255\n", "exit=255", 255),
                ("malformed-input", "invalid\n", "exit=2", 2),
            ]
        ],
        fuzz_cases=0,
        benchmark_repeats=1,
    )


async def collector_fault(mode: str) -> dict:
    """Invoke the real worker/Coverlet with one trusted collector-only fault, preserving sandbox flags."""
    require(mode in {"invalid-option", "unwritable-output", "timeout"}, "Unknown collector fault")
    project = Project(
        title="Controlled collector failure",
        language="csharp",
        entry="Program.cs",
        files=[{"name": "Program.cs", "content": 'Console.WriteLine("collector-control");\n'}],
        cases=[{"name": "healthy-target", "stdin": "", "stdout": "collector-control", "exit_code": 0}],
        fuzz_cases=0,
        benchmark_repeats=1,
    )
    # This fixed CI probe wraps only the existing trusted execute callback. It
    # does not add an application API or allow source files to select commands.
    program = """import sys,json
from pathlib import Path
sys.path.insert(0,"/opt")
import worker
from csharp_coverage_bridge import read_observation
original=worker.execute
MODE=MODE_VALUE
def collect(argv,*args,**kwargs):
    if argv and argv[0]=="/opt/coverlet/coverlet":
        if MODE=="invalid-option":
            argv=[*argv,"--cfs-intentionally-invalid-collector-option"]
        elif MODE=="unwritable-output":
            argv=list(argv)
            argv[argv.index("--output")+1]="/opt/cfs-intentionally-unwritable-coverage.xml"
        else:
            kwargs["timeout"]=0.001
        observed=original(argv,*args,**kwargs)
        text=observed.get("stdout","")+observed.get("stderr","")
        evidence={"exit_code":observed.get("exit_code"),"timeout":observed.get("timeout",False),"option_rejected":"Unrecognized" in text and "--cfs-intentionally-invalid-collector-option" in text,"collector_tail":text[-1024:],"valid_target_observation":False}
        for request in Path("/tmp/project/.analysis").glob("csharp-request-*.json"):
            try:
                record=read_observation(request,json.loads(request.read_text()))
                evidence.update(valid_target_observation=True,target_exit_code=record["target_exit_code"])
            except (OSError,ValueError):
                continue
        print("CFS_COLLECTOR_FAULT="+json.dumps(evidence),flush=True)
        return observed
    return original(argv,*args,**kwargs)
worker.execute=collect
worker.main()
""".replace("MODE_VALUE", repr(mode))
    name = "code-flow-csharp-fault-" + uuid4().hex
    with tempfile.TemporaryDirectory(prefix="code-flow-csharp-fault-") as directory:
        root = Path(directory)
        (root / "job.json").write_text(project.model_dump_json(), encoding="utf-8")
        argv = execution.container_arguments(root, name)
        argv.insert(-1, "--entrypoint=python")
        argv += ["-I", "-c", program]
        try:
            status, output = await execution.command(argv)
            require(status == 0, "Collector fault worker failed outside its report contract")
            results = [
                line.removeprefix("STUDIO_RESULT=")
                for line in output.splitlines()
                if line.startswith("STUDIO_RESULT=")
            ]
            observations = [
                line.removeprefix("CFS_COLLECTOR_FAULT=")
                for line in output.splitlines()
                if line.startswith("CFS_COLLECTOR_FAULT=")
            ]
            require(len(results) == len(observations) == 1, "Collector fault evidence is missing/ambiguous")
            result, observed = json.loads(results[0]), json.loads(observations[0])
            return {"fault": mode, "actual_collector": observed, "worker_result": result}
        finally:
            with contextlib.suppress(OSError, TimeoutError, ValueError):
                await execution.command(
                    [execution.DOCKER, "rm", "--force", name], timeout=10, output_limit=4096
                )


def validate_collector_fault(record: dict) -> None:
    """Require a real observed fault before calling its correctly blocked coverage a pass."""
    mode, observed, result = record["fault"], record["actual_collector"], record["worker_result"]
    require(mode in {"invalid-option", "unwritable-output", "timeout"}, "Unknown collector fault")
    if mode == "timeout":
        require(observed.get("timeout") is True, "Real collector timeout was not observed")
    elif mode == "invalid-option":
        # Coverlet Main ignores the parser's return and may exit zero without
        # ever invoking its target. Missing observation must still block it.
        require(
            observed.get("option_rejected") is True
            and observed.get("valid_target_observation") is False
            and not observed.get("timeout"),
            "Collector argument failure was not observed",
        )
    else:
        require(
            observed.get("exit_code") not in (None, 0)
            and not observed.get("timeout")
            and observed.get("valid_target_observation") is True
            and observed.get("target_exit_code") == 0,
            "Post-target collector report-write failure was not observed",
        )
    require(
        result.get("tool_status") == "completed"
        and result.get("checks", {}).get("passed") == 1
        and result["checks"].get("failed") == 0,
        "Fault injection also changed healthy target behavior",
    )
    require(
        result.get("coverage", {}).get("status") == "blocked",
        "Collector failure was falsely accepted as measured coverage",
    )


async def checks(record: dict, output: Path) -> None:
    """Keep real target, mismatched expectation and real collector failures separate in evidence."""

    def save():
        """Retain each completed synthetic case before any subsequent assertion can fail."""
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        temporary.replace(output)

    project = exit_project()
    result = await execution.run(project, local_only=True)
    record["exact_exits"] = {"project": project.model_dump(), "result": result}
    save()
    validate_positive(result, project)
    require(
        result["coverage"]["status"] == "measured"
        and [case["target_exit_code"] for case in result["coverage"]["cases"]] == [0, 1, 2, 7, 255, 2],
        "Instrumented target exit statuses were collapsed or coverage remains partial",
    )

    changed = project.model_dump()
    changed["cases"] = [{"name": "unexpected-nonzero", "stdin": "7\n", "stdout": "exit=7", "exit_code": 2}]
    unexpected = await execution.run(Project.model_validate(changed), local_only=True)
    record["unexpected_exit"] = unexpected
    save()
    require(
        unexpected.get("tool_status") == "completed"
        and unexpected.get("checks", {}).get("failed") == 1
        and unexpected["checks"].get("passed") == 0,
        "Unexpected target exit was not a failed case",
    )
    case = unexpected.get("coverage", {}).get("cases", [{}])[0]
    require(
        unexpected["coverage"].get("status") == "partial"
        and case.get("exit_code") == case.get("target_exit_code") == 7
        and case.get("expected_exit_code") == 2
        and case.get("collector_exit_code") == 0,
        "Unexpected target and collector outcomes were confused",
    )

    changed["files"] = [
        {
            "name": "Program.cs",
            "content": 'throw new InvalidOperationException("Synthetic C# runtime failure");\n',
            "encoding": "text",
        }
    ]
    changed["cases"] = [
        {"name": "unexpected-exception", "stdin": "", "stdout": "unreachable", "exit_code": 0}
    ]
    fault = await execution.run(Project.model_validate(changed), local_only=True)
    record["unexpected_exception"] = fault
    save()
    require(
        fault.get("checks", {}).get("failed") == 1
        and fault["checks"]["cases"][0].get("exit_code") not in (None, 0)
        and "Synthetic C# runtime failure" in fault["checks"]["cases"][0].get("stderr", ""),
        "Authored runtime exception was not observed",
    )
    require(
        fault.get("coverage", {}).get("status") in {"partial", "blocked"},
        "Unexpected exception was falsely measured as a completed approved run",
    )

    for mode in ("invalid-option", "unwritable-output", "timeout"):
        record["collector_" + mode] = await collector_fault(mode)
        save()
        validate_collector_fault(record["collector_" + mode])
    record["acceptance"] = "passed"
    save()


def main() -> None:
    """Refuse local Docker; identify the exact current runtime and exercise the real hosted tools."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-source", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(studio.__file__).resolve().parent.parent
    identity = provenance(root, args.runtime_source, "current")
    bridge = root / "runner/csharp_coverage_bridge.py"
    record = {
        "schema": 1,
        "provenance": identity,
        "bridge_sha256": hashlib.sha256(bridge.read_bytes()).hexdigest(),
        "acceptance": "pending",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    output = args.output / "csharp-coverage.json"
    asyncio.run(checks(record, output))
    print(
        "CSHARP_COVERAGE_ACCEPTANCE="
        + json.dumps(
            {
                "source": args.runtime_source,
                "version": studio.__version__,
                "target_exits": [0, 1, 2, 7, 255, 2],
                "coverage": "measured",
                "collector_errors_and_timeout": "blocked",
                "acceptance": record["acceptance"],
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
