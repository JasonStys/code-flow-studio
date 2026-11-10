# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: measurement(monkeypatch, tmp_path, actual_exit, defect)@L31; target(argv)@L49; execute(argv, stdin, timeout, env)@L57; test_real_bridge_observation_keeps_target_nonzero_separate_from_collector(monkeypatch, tmp_path, actual_exit, expected_status)@L111; test_native_measurement_cannot_promote_bad_collection_to_coverage(monkeypatch, tmp_path, defect)@L147
# variables: project@L33; work@L38; root@L40; observed@L46; target_exits@L46; launched@L47; result@L58; destination@L61; target_args@L68; request_path@L70; request@L71; index@L72; receipt@L77; content@L79; output@L82; coverage@L105; unused@L105; coverage@L115; observed@L115; project@L115; target_exits@L115; row@L119; row@L120; file@L122; case@L124; index@L124; _project@L149; coverage@L149; observed@L149; target_exits@L149
# parameters: actual_exit@L31; defect@L31; monkeypatch@L31; tmp_path@L31; _args@L44; argv@L49; kwargs@L49; argv@L57; env@L57; stdin@L57; timeout@L57; actual_exit@L112; expected_status@L112; monkeypatch@L112; tmp_path@L112; defect@L147; monkeypatch@L147; tmp_path@L147
# </code-map>

"""Jason Stys: C# collector/target/report integration without Docker, .NET or source execution.

The actual native_checks and bridge request/observation protocol run against real
temporary files. Only the compiler, collector process and unused-tool boundary
are inert doubles; hosted CI separately proves real instrumented C# behavior.
Symbol and variable locations are maintained in docs/code-index.md.
"""

import io
import json
import shlex
import subprocess
import sys
from pathlib import Path

import pytest

from examples.projects import fixture
from runner import csharp_coverage_bridge as bridge
from runner import language_checks


def measurement(monkeypatch, tmp_path, *, actual_exit=2, defect=None):
    """Drive two independently authored cases through actual measurement and receipt readers."""
    project = fixture("csharp").model_dump()
    project["cases"] = [
        {"name": "invalid-input", "stdin": "bad \U0001f680\n", "stdout": "", "exit_code": 2},
        {"name": "valid-input", "stdin": "2\n", "stdout": "4", "exit_code": 0},
    ]
    work = tmp_path / "project"
    work.mkdir()
    root = work / ".analysis"
    monkeypatch.setattr(bridge, "ANALYSIS", root)
    monkeypatch.setattr(bridge, "ASSEMBLY", root / "csharp" / "App.dll")
    monkeypatch.setattr(
        language_checks, "unused_checks", lambda *_args: {"status": "completed", "findings": []}
    )
    observed, target_exits = [], []
    launched = {"exit": None}

    def target(argv, **kwargs):
        assert argv == [str(bridge.DOTNET), str(bridge.ASSEMBLY)]
        assert kwargs["check"] is False and type(kwargs["input"]) is bytes
        target_exits.append(launched["exit"])
        return subprocess.CompletedProcess(argv, launched["exit"])

    monkeypatch.setattr(bridge.subprocess, "run", target)

    def execute(argv, stdin="", *, timeout, env=None):
        result = {"exit_code": 0, "stdout": "", "stderr": "", "timeout": False, "output_truncated": False}
        if argv[0] == "dotnet":
            assert argv[1] == "build" and timeout == 45
            destination = Path(argv[argv.index("-o") + 1])
            destination.mkdir()
            (destination / "App.dll").write_bytes(b"inert assembly marker; never executed")
            (destination / "App.pdb").write_bytes(b"inert symbols marker")
            return result
        assert argv[0] == "/opt/coverlet/coverlet" and timeout == 20 and env == {}
        assert argv[argv.index("--target") + 1] == sys.executable
        target_args = shlex.split(argv[argv.index("--targetargs") + 1])
        assert target_args[:2] == ["-I", "/opt/csharp_coverage_bridge.py"] and len(target_args) == 3
        request_path = Path(target_args[2])
        request = json.loads(request_path.read_bytes())
        index = len(observed)
        assert request["case_index"] == index and stdin == project["cases"][index]["stdin"]
        launched["exit"] = actual_exit if index == 0 else 0
        if defect != "missing-receipt":
            assert bridge.observe(request_path, io.BytesIO(stdin.encode())) == 0
        receipt = root / request["receipt"]
        if defect == "binding-tamper":
            content = json.loads(receipt.read_bytes())
            content["source_sha256"] = "f" * 64
            receipt.write_text(json.dumps(content), encoding="utf-8")
        output = Path(argv[argv.index("--output") + 1]).with_suffix(".cobertura.xml")
        if defect != "missing-xml":
            output.write_text(
                "<coverage>"
                if defect == "bad-xml"
                else '<coverage><packages><package><classes><class filename="Program.cs"><lines>'
                '<line number="2" hits="1"/><line number="3" hits="0"/>'
                "</lines></class></classes></package></packages></coverage>",
                encoding="utf-8",
            )
        observed.append(
            {"request_path": request_path, "request": request, "receipt": receipt, "output": output}
        )
        if defect == "collector-error":
            result["exit_code"] = 1
        elif defect == "collector-missing-exit":
            result["exit_code"] = None
        elif defect == "timeout":
            result["timeout"] = True
        elif defect == "truncated":
            result["output_truncated"] = True
        return result

    coverage, unused = language_checks.native_checks(project, work, execute, ["dotnet", "compiled/App.dll"])
    assert unused == {"status": "completed", "findings": []}
    return coverage, observed, target_exits, project


@pytest.mark.parametrize("actual_exit, expected_status", [(2, "measured"), (7, "partial")])
def test_real_bridge_observation_keeps_target_nonzero_separate_from_collector(
    monkeypatch, tmp_path, actual_exit, expected_status
):
    """Only matching real observed target returns can complete the approved case set."""
    coverage, observed, target_exits, project = measurement(monkeypatch, tmp_path, actual_exit=actual_exit)
    assert coverage["status"] == expected_status and coverage["requested_cases"] == 2
    assert target_exits == [actual_exit, 0]
    assert len(observed) == len(coverage["cases"]) == 2
    assert len({row["request"]["nonce"] for row in observed}) == 2
    assert len({row["receipt"] for row in observed}) == 2
    assert coverage["tool"] == "Coverlet 8.0.1"
    file = coverage["files"][project["entry"]]
    assert file["status"] == "measured" and file["executed_lines"] == [2] and file["missing_lines"] == [3]
    for index, case in enumerate(coverage["cases"]):
        assert case["name"] == project["cases"][index]["name"]
        assert case["expected_exit_code"] == project["cases"][index]["exit_code"]
        assert case["exit_code"] == case["target_exit_code"] == target_exits[index]
        assert case["collector_exit_code"] == 0 and case["collector_output_truncated"] is False
        assert case["bridge"] == bridge.read_observation(
            observed[index]["request_path"], observed[index]["request"]
        )


@pytest.mark.parametrize(
    "defect",
    [
        "collector-error",
        "collector-missing-exit",
        "timeout",
        "truncated",
        "missing-receipt",
        "binding-tamper",
        "missing-xml",
        "bad-xml",
    ],
)
def test_native_measurement_cannot_promote_bad_collection_to_coverage(monkeypatch, tmp_path, defect):
    """Valid target proof cannot mask collector failure; valid XML cannot replace target proof."""
    coverage, observed, target_exits, _project = measurement(monkeypatch, tmp_path, defect=defect)
    assert coverage["status"] == "blocked" and coverage["reason"].startswith("Native coverage unavailable:")
    assert len(observed) == 1
    if defect in {"collector-error", "collector-missing-exit", "timeout", "truncated"}:
        # The negative intentionally has BOTH valid target proof and XML.
        assert target_exits == [2] and observed[0]["output"].exists()
        assert (
            bridge.read_observation(observed[0]["request_path"], observed[0]["request"])["target_exit_code"]
            == 2
        )
    elif defect == "missing-receipt":
        assert target_exits == [] and observed[0]["output"].exists() and not observed[0]["receipt"].exists()
