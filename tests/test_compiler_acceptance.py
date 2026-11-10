# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: complete_result(project)@L24; test_practical_matrix_is_complete_and_independent()@L70; test_positive_validator_rejects_incomplete_or_fabricated_evidence(defect)@L114; test_exact_compiler_location_and_nonexecution_are_required()@L168; test_runtime_failure_is_distinct_from_incorrect_oracle()@L201; test_real_execution_guard_refuses_this_pc_before_subprocess(monkeypatch)@L237
# variables: content@L26; case@L42; case@L46; language@L74; project@L75; case@L77; duplicate@L81; project@L116; result@L117; project@L170; result@L171; defect@L189; changed@L190; project@L203; result@L204; wrong@L226
# parameters: project@L24; defect@L114; monkeypatch@L237
# </code-map>

"""Jason Stys: reject fabricated/incomplete compiler evidence without using local Docker."""

import copy
import hashlib
import json
import math
from pathlib import Path

import pytest

from examples.practical_projects import CASES, PROGRAMS, RUNTIME_FAILURES, SYNTAX_FAILURES, practical_project
from scripts.compiler_acceptance import negative_project, provenance, validate_negative, validate_positive
from studio.models import LANGUAGES


def complete_result(project):
    """A minimal synthetic evidence record for validator mutation tests, never toolchain proof."""
    content = project.files[0].content
    return {
        "tool_status": "completed",
        "compilation": {"exit_code": 0},
        "checks": {
            "passed": len(project.cases),
            "failed": 0,
            "cases": [
                {
                    "name": case.name,
                    "stdout": case.stdout,
                    "exit_code": case.exit_code,
                    "passed": True,
                    "timeout": False,
                    "output_truncated": False,
                }
                for case in project.cases
            ],
        },
        "oracle_hash": hashlib.sha256(
            json.dumps([case.model_dump() for case in project.cases], sort_keys=True).encode()
        ).hexdigest(),
        "environment": {"language": project.language},
        "benchmark": {
            "samples_ms": [1.0] * len(project.cases) * project.benchmark_repeats,
            "max_rss_kib": 1024,
        },
        "coverage": {
            "status": "measured",
            "files": {
                project.entry: {
                    "status": "measured",
                    "source_sha256": hashlib.sha256(content.encode()).hexdigest(),
                    "executed_lines": [1],
                    "missing_lines": [],
                    "summary": {"covered_lines": 1, "missing_lines": 0, "num_statements": 1},
                }
            },
        },
        "unused": {"status": "completed"},
        "static": {"files": {project.entry: {"parsed": True}}},
    }


def test_practical_matrix_is_complete_and_independent():
    """Every executable adapter has several explicit independent oracles and both control sources."""
    assert set(PROGRAMS) == set(CASES) == set(RUNTIME_FAILURES) == set(LANGUAGES)
    assert set(SYNTAX_FAILURES) == set(LANGUAGES) - {"sql"}
    for language in LANGUAGES:
        project = practical_project(language)
        assert project.language == language and len(project.cases) == 6
        assert len({case.name for case in project.cases}) == 6
        assert project.cases[0].exit_code == 0
        assert project.fuzz_cases == 0 and project.benchmark_repeats == 1
        validate_positive(complete_result(project), project)
        duplicate = practical_project(language)
        duplicate.cases[0].stdout = "changed only this instance"
        assert practical_project(language).cases[0].stdout != duplicate.cases[0].stdout


@pytest.mark.parametrize(
    "defect",
    [
        "blocked",
        "compile",
        "missing-case",
        "wrong-output",
        "wrong-exit",
        "false-pass",
        "timeout",
        "truncated-output",
        "wrong-oracle-hash",
        "wrong-adapter",
        "missing-sample",
        "nan-time",
        "missing-rss",
        "partial-coverage",
        "wrong-source",
        "unmeasured-entry",
        "bad-line",
        "missing-unused",
        "truncated-locations",
        "overlapping-coverage",
        "duplicate-coverage",
        "inconsistent-coverage",
        "truncated-compilation",
    ],
)
def test_positive_validator_rejects_incomplete_or_fabricated_evidence(defect):
    """Mutate concrete report fields so a green workflow cannot mean just 'worker returned JSON'."""
    project = practical_project("typescript")
    result = complete_result(project)
    if defect == "blocked":
        result["tool_status"] = "blocked"
    elif defect == "compile":
        result["compilation"]["exit_code"] = 2
    elif defect == "missing-case":
        result["checks"]["cases"].pop()
    elif defect == "wrong-output":
        result["checks"]["cases"][0]["stdout"] = "incorrect"
    elif defect == "wrong-exit":
        result["checks"]["cases"][0]["exit_code"] = 9
    elif defect == "false-pass":
        result["checks"]["cases"][0]["passed"] = False
    elif defect == "timeout":
        result["checks"]["cases"][0]["timeout"] = True
    elif defect == "truncated-output":
        result["checks"]["cases"][0]["output_truncated"] = True
    elif defect == "wrong-oracle-hash":
        result["oracle_hash"] = "0" * 64
    elif defect == "wrong-adapter":
        result["environment"]["language"] = "python"
    elif defect == "missing-sample":
        result["benchmark"]["samples_ms"].pop()
    elif defect == "nan-time":
        result["benchmark"]["samples_ms"][0] = math.nan
    elif defect == "missing-rss":
        result["benchmark"]["max_rss_kib"] = None
    elif defect == "partial-coverage":
        result["coverage"]["status"] = "partial"
    elif defect == "wrong-source":
        result["coverage"]["files"][project.entry]["source_sha256"] = "0" * 64
    elif defect == "unmeasured-entry":
        result["coverage"]["files"][project.entry]["executed_lines"] = []
    elif defect == "bad-line":
        result["coverage"]["files"][project.entry]["missing_lines"] = [999999]
    elif defect == "missing-unused":
        result["unused"]["status"] = "blocked"
    elif defect == "truncated-locations":
        result["diagnostics_truncated"] = True
    elif defect == "overlapping-coverage":
        result["coverage"]["files"][project.entry]["missing_lines"] = [1]
    elif defect == "duplicate-coverage":
        result["coverage"]["files"][project.entry]["executed_lines"] = [1, 1]
    elif defect == "inconsistent-coverage":
        result["coverage"]["files"][project.entry]["summary"]["num_statements"] = 99
    elif defect == "truncated-compilation":
        result["compilation"]["output_truncated"] = True
    with pytest.raises(ValueError):
        validate_positive(result, project)


def test_exact_compiler_location_and_nonexecution_are_required():
    """A malformed C++ target must fail compilation at its authored line before any case executes."""
    project = negative_project(practical_project("cpp"), "syntax-error")
    result = {
        "tool_status": "compile-error",
        "compilation": {"exit_code": 1},
        "checks": {"passed": 0, "failed": 0, "cases": []},
        "coverage": {"status": "blocked"},
        "unused": {"status": "blocked"},
        "environment": {"language": project.language},
        "oracle_hash": complete_result(project)["oracle_hash"],
        "diagnostics": [
            {
                "file": project.entry,
                "line": SYNTAX_FAILURES["cpp"]["line"],
                "source_sha256": hashlib.sha256(project.files[0].content.encode()).hexdigest(),
                "stage": "compilation",
            }
        ],
    }
    validate_negative(result, project, "syntax-error")
    for defect in ("missing-location", "executed-uncompiled", "invented-coverage"):
        changed = copy.deepcopy(result)
        if defect == "missing-location":
            changed["diagnostics"] = []
        elif defect == "executed-uncompiled":
            changed["checks"]["cases"] = [{"passed": False}]
        else:
            changed["coverage"]["status"] = "measured"
        with pytest.raises(ValueError):
            validate_negative(changed, project, "syntax-error")


def test_runtime_failure_is_distinct_from_incorrect_oracle():
    """A failing expected-output comparison alone cannot prove a program runtime fault."""
    project = negative_project(practical_project("python"), "runtime-error")
    result = {
        "tool_status": "completed",
        "compilation": {"exit_code": 0},
        "environment": {"language": project.language},
        "oracle_hash": complete_result(project)["oracle_hash"],
        "checks": {
            "passed": 0,
            "failed": 1,
            "cases": [
                {
                    "name": "runtime-error",
                    "passed": False,
                    "exit_code": 1,
                    "stderr": "RuntimeError: Synthetic runtime failure",
                }
            ],
        },
    }
    validate_negative(result, project, "runtime-error")
    result["checks"]["cases"][0]["exit_code"] = 0
    with pytest.raises(ValueError):
        validate_negative(result, project, "runtime-error")
    wrong = negative_project(practical_project("python"), "wrong-oracle")
    result["oracle_hash"] = complete_result(wrong)["oracle_hash"]
    result["checks"]["cases"][0].update(
        {"name": "wrong-oracle", "stdout": practical_project("python").cases[0].stdout}
    )
    validate_negative(result, wrong, "wrong-oracle")
    result["checks"]["cases"][0]["stdout"] = "A second independent implementation bug"
    with pytest.raises(ValueError, match="implementation/output fault"):
        validate_negative(result, wrong, "wrong-oracle")


def test_real_execution_guard_refuses_this_pc_before_subprocess(monkeypatch):
    """No local Docker command runs when the hosted acceptance entry point is invoked accidentally."""
    monkeypatch.delenv("GITHUB_ACTIONS", raising=False)
    with pytest.raises(ValueError, match="GitHub-hosted Linux"):
        provenance(Path.cwd(), "0" * 40, "release-0.4.2")
