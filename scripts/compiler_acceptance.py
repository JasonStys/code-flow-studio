# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L348
# functions: require(condition, message)@L45; source_digest(text)@L51; source_line_count(text)@L56; validate_coverage_completion(coverage, project, historical_source)@L61; validate_locations(result, project)@L136; validate_positive(result, project, historical_source)@L149; negative_project(project, kind)@L250; validate_negative(result, project, kind)@L269; __init__(self, output, provenance)@L351; record(self, language, kind, project, result, error)@L358; save(self)@L380; broker_scenarios(evidence)@L407; anchor_scenarios(evidence)@L434; private_scenarios(evidence)@L465; provenance(runtime, expected_source, lane)@L575; toolchain_versions()@L630; main()@L675
# variables: RELEASE_SOURCE@L40; RELEASE_WORKER_SHA256@L41; CSHARP_TARGET@L42; wrapped@L66; cases@L68; actual@L73; expected@L73; index@L73; wrapped@L90; bridge@L100; source_hash@L101; file@L103; input_bytes@L109; expected_bridge@L110; expected_status@L129; file@L138; sources@L138; item@L140; line@L141; name@L141; compilation@L152; checks@L159; observed@L161; actual@L163; expected@L163; oracle@L173; case@L174; benchmark@L178; samples@L179; value@L182; coverage@L188; entry@L191; content@L192; file@L192; measured@L198; name@L198; file@L201; source@L201; line@L206; executed@L208; missing@L208; summary@L214; covered@L215; extra@L223; first@L227; data@L252; replacement@L258; expected_oracle@L280; case@L281; checks@L284; line@L302; item@L308; case@L319; exit_code@L326; marker@L331; row@L362; key@L376; record@L382; temporary@L383; lines@L386; row@L394; checks@L395; lines@L399; language@L409; baseline@L410; kind@L411; project@L414; result@L415; error@L416; result@L418; error@L430; language@L436; missing_line@L437; project@L437; unused_line@L437; result@L438; error@L439; result@L441; item@L456; error@L461; credentials@L467; key@L468; directory@L469; app@L470; client@L475; jobs@L483; language@L484; project@L485; result@L486; error@L487; response@L489; revision@L491; response@L492; job@L494; deadline@L495; response@L497; report@L499; result@L504; exported@L512; html@L517; error@L524; archives@L528; response@L543; job@L549; result_sha256@L549; response@L550; exported@L557; runtime@L583; source@L588; dirty@L590; worker@L600; command@L605; image@L606; commands@L632; program@L646; name@L651; directory@L652; root@L653; argv@L655; argv@L657; code@L659; output@L659; versions@L661; value@L667; parser@L677; args@L682; evidence@L683; language@L704
# parameters: condition@L45; message@L45; text@L51; text@L56; coverage@L62; historical_source@L62; project@L62; project@L136; result@L136; historical_source@L149; project@L149; result@L149; kind@L250; project@L250; kind@L269; project@L269; result@L269; output@L351; provenance@L351; self@L351; error@L359; kind@L359; language@L359; project@L359; result@L359; self@L359; self@L380; evidence@L407; evidence@L434; evidence@L465; expected_source@L575; lane@L575; runtime@L575
# </code-map>

"""Jason Stys: real hosted compiler scenarios, independent oracles and private history.

Only main() is hosted-only. Pure evidence validators can run without Docker.
Source maps in this file and docs/code-index.md describe exact declarations.
"""

import argparse
import ast
import asyncio
import base64
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from uuid import uuid4

from fastapi.testclient import TestClient

import studio
from examples.language_locations import SAMPLES, location_fixture
from examples.practical_projects import RUNTIME_FAILURES, SYNTAX_FAILURES, practical_project
from studio import execution
from studio.models import LANGUAGES, Project
from studio.private_api import create_private_app

RELEASE_SOURCE = "eb9b1cd0c3e3fd1e70e397edeffb059073464f74"
RELEASE_WORKER_SHA256 = "750b665e545b7cf0806d4c493db86174f7f4e7ab2218aa239718e652ccdce158"
CSHARP_TARGET = "/tmp/project/.analysis/csharp/App.dll"  # noqa: S108 -- inert original worker path, never a host file.


def require(condition: bool, message: str) -> None:
    """Fail explicitly even under optimized Python; never downgrade a missing tool to success."""
    if not condition:
        raise ValueError(message)


def source_digest(text: str) -> str:
    """Bind evidence to exact UTF-8 bytes, including its original newlines."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def source_line_count(text: str) -> int:
    """Use the app's original-source convention, retaining an empty terminal line for EOF opcodes."""
    return len(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))


def validate_coverage_completion(
    coverage: dict, project: Project, historical_source: str | None = None
) -> None:
    """Require exact current target/collector evidence; preserve only the pinned historical baseline."""
    require(historical_source in (None, RELEASE_SOURCE), "Unknown historical coverage policy")
    wrapped = False
    if project.language != "python":
        cases = coverage.get("cases", [])
        require(
            coverage.get("requested_cases") == len(project.cases) and len(cases) == len(project.cases),
            "Missing instrumented case evidence",
        )
        for index, (expected, actual) in enumerate(zip(project.cases, cases, strict=True)):
            require(
                actual.get("name") == expected.name
                and actual.get("expected_exit_code") == expected.exit_code
                and not actual.get("timeout"),
                "Instrumented case identity/deadline mismatch",
            )
            if actual.get("exit_code") != expected.exit_code:
                require(
                    historical_source == RELEASE_SOURCE
                    and project.language == "csharp"
                    and coverage.get("tool") == "Coverlet 8.0.1"
                    and expected.exit_code != 0
                    and actual.get("exit_code") == 1
                    and "Generating report" in actual.get("collector_messages", ""),
                    "Unexpected instrumented execution failure",
                )
                wrapped = True
            if project.language == "csharp" and historical_source is None:
                require(
                    type(actual.get("collector_exit_code")) is int
                    and actual["collector_exit_code"] == 0
                    and type(actual.get("target_exit_code")) is int
                    and actual["target_exit_code"] == actual.get("exit_code")
                    and not actual.get("collector_output_truncated"),
                    "Current C# collector/target exits are not independently complete",
                )
                bridge = actual.get("bridge", {})
                source_hash = source_digest(
                    json.dumps(
                        [file.model_dump() for file in project.files],
                        sort_keys=True,
                        separators=(",", ":"),
                        ensure_ascii=False,
                    )
                )
                input_bytes = expected.stdin.encode("utf-8")
                expected_bridge = (
                    Path(studio.__file__).resolve().parent.parent / "runner/csharp_coverage_bridge.py"
                )
                require(
                    type(bridge.get("schema")) is int
                    and bridge["schema"] == 1
                    and type(bridge.get("case_index")) is int
                    and bridge["case_index"] == index
                    and bridge.get("target") == CSHARP_TARGET
                    and bridge.get("source_sha256") == source_hash
                    and bridge.get("stdin_sha256") == hashlib.sha256(input_bytes).hexdigest()
                    and type(bridge.get("stdin_bytes")) is int
                    and bridge["stdin_bytes"] == len(input_bytes)
                    and type(bridge.get("target_exit_code")) is int
                    and bridge["target_exit_code"] == expected.exit_code
                    and bridge.get("bridge_sha256")
                    == hashlib.sha256(expected_bridge.read_bytes()).hexdigest(),
                    "Current C# bridge is not bound to this source/case/input/helper",
                )
    expected_status = "partial" if wrapped else "measured"
    require(
        coverage.get("status") == expected_status,
        "Coverage completion status disagrees with actual collector exits",
    )


def validate_locations(result: dict, project: Project) -> None:
    """Accept only reported in-range references to the supplied source snapshot."""
    sources = {file.name: file.content for file in project.files if file.encoding == "text"}
    require(not result.get("diagnostics_truncated"), "Diagnostic evidence was truncated")
    for item in result.get("diagnostics", []):
        name, line = item.get("file"), item.get("line")
        require(name in sources, "Diagnostic references an unknown file")
        require(
            type(line) is int and 0 < line <= source_line_count(sources[name]), "Diagnostic line is invalid"
        )
        require(item.get("source_sha256") == source_digest(sources[name]), "Diagnostic source hash mismatch")


def validate_positive(result: dict, project: Project, *, historical_source: str | None = None) -> None:
    """Require actual compilation, every approved output, measurements and source-bound coverage."""
    require(result.get("tool_status") == "completed", "Worker did not complete")
    compilation = result.get("compilation", {})
    require(
        compilation.get("exit_code") == 0
        and not compilation.get("timeout")
        and not compilation.get("output_truncated"),
        "Compilation failed or was truncated",
    )
    checks = result.get("checks", {})
    require(checks.get("passed") == len(project.cases) and checks.get("failed") == 0, "Approved cases failed")
    observed = checks.get("cases", [])
    require(len(observed) == len(project.cases), "Missing or extra execution results")
    for expected, actual in zip(project.cases, observed, strict=True):
        require(
            actual.get("name") == expected.name and actual.get("passed") is True,
            "Case identity/pass mismatch",
        )
        require(actual.get("exit_code") == expected.exit_code, "Wrong target exit status")
        require(actual.get("stdout", "").strip() == expected.stdout.strip(), "Wrong target output")
        require(
            not actual.get("timeout") and not actual.get("output_truncated"), "Execution evidence incomplete"
        )
    oracle = hashlib.sha256(
        json.dumps([case.model_dump() for case in project.cases], sort_keys=True).encode()
    ).hexdigest()
    require(result.get("oracle_hash") == oracle, "Approved oracle identity changed")
    require(result.get("environment", {}).get("language") == project.language, "Wrong language adapter")
    benchmark = result.get("benchmark", {})
    samples = benchmark.get("samples_ms", [])
    require(len(samples) == len(project.cases) * project.benchmark_repeats, "Missing benchmark repetitions")
    require(
        all(type(value) in (int, float) and math.isfinite(value) and value >= 0 for value in samples),
        "Invalid timing sample",
    )
    require(
        type(benchmark.get("max_rss_kib")) is int and benchmark["max_rss_kib"] > 0, "Missing measured RSS"
    )
    coverage = result.get("coverage", {})
    validate_coverage_completion(coverage, project, historical_source)
    require(not coverage.get("locations_truncated"), "Coverage locations were truncated")
    entry = coverage.get("files", {}).get(project.entry, {})
    content = next(file.content for file in project.files if file.name == project.entry)
    require(
        entry.get("status") == "measured" and entry.get("executed_lines"), "Entry has no executed coverage"
    )
    require(entry.get("source_sha256") == source_digest(content), "Coverage source hash mismatch")
    require(not entry.get("truncated"), "Entry coverage was truncated")
    for name, measured in coverage.get("files", {}).items():
        if measured.get("status") != "measured":
            continue
        source = next((file.content for file in project.files if file.name == name), None)
        require(
            source is not None and measured.get("source_sha256") == source_digest(source),
            "Unknown measured source",
        )
        for line in measured.get("executed_lines", []) + measured.get("missing_lines", []):
            require(type(line) is int and 0 < line <= source_line_count(source), "Coverage line out of range")
        executed, missing = measured.get("executed_lines", []), measured.get("missing_lines", [])
        require(
            len(executed) == len(set(executed)) and len(missing) == len(set(missing)),
            "Duplicate coverage line",
        )
        require(not set(executed).intersection(missing), "Coverage line is both executed and missing")
        summary = measured.get("summary", {})
        covered = summary.get("covered_lines")
        require(
            type(covered) is int
            and covered >= 0
            and summary.get("missing_lines") == len(missing)
            and summary.get("num_statements") == covered + len(missing),
            "Coverage statement counts disagree",
        )
        extra = len(executed) - covered
        if extra and project.language == "python":
            # coverage.py retains the module docstring trace event, but excludes
            # that nonstatement from its executable-statement denominator.
            first = ast.parse(source).body[0]
            require(
                extra == 1
                and isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
                and first.lineno in executed,
                "Unexplained Python trace/statement count difference",
            )
        else:
            require(extra == 0, "Coverage counts disagree with retained locations")
    if project.language != "python":
        require(
            result.get("unused", {}).get("status") == "completed", "Native unused-code tool did not complete"
        )
    else:
        require(
            result.get("static", {}).get("files", {}).get(project.entry, {}).get("parsed") is True,
            "Python AST was not parsed",
        )
    validate_locations(result, project)


def negative_project(project: Project, kind: str) -> Project:
    """Make independent negative controls; never alter an approved production revision."""
    data = project.model_dump()
    data["cases"] = [data["cases"][0]]
    data["cases"][0]["name"] = kind
    if kind == "wrong-oracle":
        data["cases"][0]["stdout"] = "INTENTIONALLY INCORRECT EXPECTED OUTPUT"
    else:
        replacement = (
            SYNTAX_FAILURES[project.language]["content"]
            if kind == "syntax-error"
            else RUNTIME_FAILURES[project.language]
        )
        data["files"] = [{"name": project.entry, "content": replacement, "encoding": "text"}]
        data["cases"][0]["stdout"] = "UNREACHABLE SUCCESS OUTPUT"
        data["cases"][0]["exit_code"] = 0
    return Project.model_validate(data)


def validate_negative(result: dict, project: Project, kind: str) -> None:
    """A deliberately bad target/oracle must be detected, rather than making CI falsely green."""
    validate_locations(result, project)
    require(
        not result.get("compilation", {}).get("timeout")
        and not result.get("compilation", {}).get("output_truncated"),
        "Negative compilation was interrupted or truncated",
    )
    require(
        result.get("environment", {}).get("language") == project.language, "Wrong negative-control adapter"
    )
    expected_oracle = hashlib.sha256(
        json.dumps([case.model_dump() for case in project.cases], sort_keys=True).encode()
    ).hexdigest()
    require(result.get("oracle_hash") == expected_oracle, "Negative-control oracle identity changed")
    checks = result.get("checks", {})
    if kind == "syntax-error":
        require(
            result.get("tool_status") == "compile-error", "Invalid source was not rejected at compilation"
        )
        require(result.get("compilation", {}).get("exit_code") not in (None, 0), "Missing compiler failure")
        require(
            checks.get("passed") == 0 and checks.get("failed") == 0 and not checks.get("cases"),
            "Uncompiled source was executed",
        )
        require(
            result.get("coverage", {}).get("status") == "blocked",
            "Failed compilation claimed measured coverage",
        )
        require(
            result.get("unused", {}).get("status") == "blocked",
            "Failed compilation claimed unused-code completion",
        )
        line = SYNTAX_FAILURES[project.language]["line"]
        require(
            any(
                item.get("file") == project.entry
                and item.get("line") == line
                and item.get("stage") == "compilation"
                for item in result.get("diagnostics", [])
            ),
            "Compiler failure lacks its independently specified exact source line",
        )
    else:
        require(result.get("tool_status") == "completed", "Negative target did not reach execution")
        require(result.get("compilation", {}).get("exit_code") == 0, "Runtime/oracle control did not compile")
        require(
            checks.get("passed") == 0 and checks.get("failed") == 1 and len(checks.get("cases", [])) == 1,
            "Bad execution/oracle was not rejected",
        )
        case = checks["cases"][0]
        require(case.get("name") == project.cases[0].name, "Wrong negative-control case identity")
        require(
            case.get("passed") is False and not case.get("timeout") and not case.get("output_truncated"),
            "Negative result is not a completed observed failure",
        )
        if kind == "runtime-error":
            exit_code = 1 if project.language in {"python", "javascript", "typescript", "sql"} else 7
            require(
                case.get("exit_code") == exit_code,
                "Faulting program did not produce its authored failure exit",
            )
            marker = "missing_table" if project.language == "sql" else "Synthetic runtime failure"
            if project.language in {"python", "javascript", "typescript", "sql"}:
                require(
                    marker in case.get("stderr", ""),
                    "Runtime diagnostic does not identify the authored fault",
                )
        else:
            require(
                case.get("exit_code") == project.cases[0].exit_code,
                "Wrong-oracle control also had a runtime fault",
            )
            require(
                case.get("stdout", "").strip() == practical_project(project.language).cases[0].stdout.strip(),
                "Wrong-oracle control also had an implementation/output fault",
            )


class Evidence:
    """Incrementally preserve synthetic results and fail closed if any language or scenario is missing."""

    def __init__(self, output: Path, provenance: dict):
        """output is a dedicated CI report directory; provenance identifies tested code and worker."""
        self.output, self.provenance = output, provenance
        self.rows: list[dict] = []
        self.errors: list[str] = []
        output.mkdir(parents=True, exist_ok=True)

    def record(
        self, language: str, kind: str, project: Project, result: dict, error: str | None = None
    ) -> None:
        """Persist before continuing so a later tool failure cannot erase earlier evidence."""
        row = {
            "language": language,
            "kind": kind,
            "acceptance": "failed" if error else "passed",
            "project": project.model_dump(),
            "result": result,
            "error": error,
        }
        self.rows.append(row)
        if error:
            self.errors.append(language + "/" + kind + ": " + error)
        self.save()
        print(
            "COMPILER_SCENARIO="
            + json.dumps({key: row[key] for key in ("language", "kind", "acceptance", "error")}),
            flush=True,
        )

    def save(self) -> None:
        """Write a replace-atomic JSON receipt and a small human-readable result table."""
        record = {"schema": 1, "provenance": self.provenance, "scenarios": self.rows, "errors": self.errors}
        temporary = self.output / "results.tmp"
        temporary.write_text(json.dumps(record, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        temporary.replace(self.output / "results.json")
        lines = [
            "# Hosted compiler and execution validation",
            "",
            "Runtime source: `" + self.provenance["runtime_source"] + "`",
            "",
            "| Language | Scenario | Acceptance | Target passed / failed | Coverage |",
            "|---|---|---|---|---|",
        ]
        for row in self.rows:
            checks = row["result"].get("checks", {})
            lines.append(
                f"| {row['language']} | {row['kind']} | {row['acceptance']} | {checks.get('passed', '—')} / {checks.get('failed', '—')} | {row['result'].get('coverage', {}).get('status', '—')} |"
            )
        lines += [
            "",
            "Negative-control acceptance means the intentionally invalid target/oracle was correctly rejected. Completion alone is not a correctness pass. Timings include process startup and are not cross-language performance rankings.",
            "",
        ]
        (self.output / "summary.md").write_text("\n".join(lines), encoding="utf-8")


async def broker_scenarios(evidence: Evidence) -> None:
    """Run positive, incorrect-oracle, compiler-error and runtime-error controls for all adapters."""
    for language in LANGUAGES:
        baseline = practical_project(language)
        for kind in ("positive", "wrong-oracle", "syntax-error", "runtime-error"):
            if kind == "syntax-error" and language not in SYNTAX_FAILURES:
                continue  # SQLite parses/runs the schema at execution, not a separate compiler phase.
            project = baseline if kind == "positive" else negative_project(baseline, kind)
            result: dict = {}
            error = None
            try:
                result = await execution.run(project, local_only=True)
                if kind == "positive":
                    validate_positive(
                        result,
                        project,
                        historical_source=RELEASE_SOURCE
                        if evidence.provenance["lane"] == "release-0.4.2"
                        else None,
                    )
                else:
                    validate_negative(result, project, kind)
            except (OSError, ValueError, KeyError, TypeError) as failure:
                error = str(failure)[:400]
            evidence.record(language, kind, project, result, error)


async def anchor_scenarios(evidence: Evidence) -> None:
    """Retain independent exact unused/uncovered anchors alongside realistic multi-case execution."""
    for language in SAMPLES:
        project, unused_line, missing_line = location_fixture(language)
        result: dict = {}
        error = None
        try:
            result = await execution.run(project, local_only=True)
            validate_positive(
                result,
                project,
                historical_source=RELEASE_SOURCE if evidence.provenance["lane"] == "release-0.4.2" else None,
            )
            require(
                missing_line in result["coverage"]["files"][project.entry]["missing_lines"],
                "Authored uncovered anchor was not measured as missing",
            )
            require(
                any(
                    item.get("file") == project.entry
                    and item.get("line") == unused_line
                    and item.get("stage") == "unused-code"
                    for item in result.get("diagnostics", [])
                ),
                "Authored unused anchor was not detected",
            )
        except (OSError, ValueError, KeyError, TypeError) as failure:
            error = str(failure)[:400]
        evidence.record(language, "native-location", project, result, error)


def private_scenarios(evidence: Evidence) -> None:
    """Exercise realistic programs through real authenticated account API and encrypted history."""
    credentials = {"alias": "synthetic_compiler_ci", "password": "fictional-compiler-ci-password-2026"}
    key = {"key": base64.b64encode(b"k" * 32).decode(), "salt": base64.b64encode(b"s" * 16).decode()}
    with tempfile.TemporaryDirectory(prefix="code-flow-practical-account-") as directory:
        app = create_private_app(Path(directory) / "accounts", 8090)
        with TestClient(
            app,
            base_url="http://127.0.0.1:8090",
            headers={"X-CFS-Request": "v1", "Content-Type": "application/json"},
        ) as client:
            require(
                client.post("/private/register", json=credentials).status_code == 200,
                "Synthetic registration failed",
            )
            require(
                client.post("/private/unlock", json=key).status_code == 200, "Synthetic vault unlock failed"
            )
            jobs = []
            for language in LANGUAGES:
                project = practical_project(language)
                result: dict = {}
                error = None
                try:
                    response = client.post("/private/api/revisions", json=project.model_dump())
                    require(response.status_code == 200, "Revision save failed")
                    revision = response.json()["id"]
                    response = client.post(f"/private/api/revisions/{revision}/run", json={})
                    require(response.status_code == 200, "Compiler job queue failed")
                    job = response.json()["id"]
                    deadline = time.monotonic() + 180
                    while time.monotonic() < deadline:
                        response = client.get("/private/api/runs/" + job)
                        require(response.status_code == 200, "Compiler job poll failed")
                        report = response.json()
                        if report["status"] not in {"queued", "running"}:
                            break
                        time.sleep(0.5)
                    require(report["status"] == "completed", "Private job did not complete")
                    result = report["result"]
                    validate_positive(
                        result,
                        project,
                        historical_source=RELEASE_SOURCE
                        if evidence.provenance["lane"] == "release-0.4.2"
                        else None,
                    )
                    exported = client.get(f"/private/api/runs/{job}/report?format=json")
                    require(
                        exported.status_code == 200 and exported.json()["result"] == result,
                        "JSON export differs from observed execution",
                    )
                    html = client.get(f"/private/api/runs/{job}/report?format=html")
                    require(
                        html.status_code == 200 and "text/html" in html.headers.get("content-type", ""),
                        "HTML report export failed",
                    )
                    jobs.append((job, source_digest(json.dumps(result, sort_keys=True, allow_nan=False))))
                except (OSError, ValueError, KeyError, TypeError) as failure:
                    error = str(failure)[:400]
                evidence.record(language, "private-api", project, result, error)
            require(client.post("/private/lock", json={}).status_code == 200, "Private history seal failed")
            require(not app.state.manager.active.exists(), "Plaintext workspace retained after lock")
            archives = list(app.state.manager.archives.glob("*.cfsvault"))
            require(len(archives) == 1 and archives[0].stat().st_size > 0, "Encrypted archive missing")
            require(client.post("/private/logout", json={}).status_code == 200, "Synthetic logout failed")
            require(
                client.get("/private/api/revisions").status_code == 401,
                "History remained visible after logout",
            )
            require(
                client.post("/private/login", json=credentials).status_code == 200,
                "Existing synthetic account login failed",
            )
            require(
                client.post("/private/unlock", json=key).status_code == 200,
                "Saved encrypted history did not reopen",
            )
            response = client.get("/private/api/revisions")
            require(
                response.status_code == 200 and len(response.json()) == len(LANGUAGES),
                "History lost saved revisions",
            )
            require(len(jobs) == len(LANGUAGES), "Missing successful private compiler jobs")
            for job, result_sha256 in jobs:
                response = client.get("/private/api/runs/" + job)
                require(
                    response.status_code == 200
                    and source_digest(json.dumps(response.json()["result"], sort_keys=True, allow_nan=False))
                    == result_sha256,
                    "Encrypted report identity was not retained",
                )
                exported = client.get(f"/private/api/runs/{job}/report?format=json")
                require(
                    exported.status_code == 200
                    and source_digest(json.dumps(exported.json()["result"], sort_keys=True, allow_nan=False))
                    == result_sha256,
                    "Reopened JSON export changed execution evidence",
                )
            require(
                client.post("/private/lock", json={}).status_code == 200, "Final synthetic vault lock failed"
            )
            evidence.provenance["private_history"] = {
                "login_after_logout": "passed",
                "sealed_and_reopened_reports": len(jobs),
                "plaintext_removed": not app.state.manager.active.exists(),
            }
            evidence.save()


def provenance(runtime: Path, expected_source: str, lane: str) -> dict:
    """Refuse accidental local execution or source/import/image substitutions before running programs."""
    require(
        os.environ.get("GITHUB_ACTIONS") == "true"
        and os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted"
        and sys.platform == "linux",
        "Real compiler validation runs only on GitHub-hosted Linux; local Docker is unchanged",
    )
    runtime = runtime.resolve(strict=True)
    require(
        Path(studio.__file__).resolve().parent.parent == runtime,
        "Controller imported from the wrong checkout",
    )
    source = subprocess.check_output(["git", "-C", str(runtime), "rev-parse", "HEAD"], text=True).strip()  # noqa: S603,S607 -- fixed CI git operation.
    require(source == expected_source and len(source) == 40, "Runtime source identity mismatch")
    dirty = subprocess.check_output(  # noqa: S603 -- fixed read-only CI git operation.
        ["git", "-C", str(runtime), "status", "--porcelain", "--untracked-files=no"],  # noqa: S607
        text=True,
    ).strip()
    require(not dirty, "Runtime tracked source is dirty")
    require(
        studio.__version__ == ("0.4.2" if lane == "release-0.4.2" else "0.4.3")
        and execution.IMAGE == f"code-flow-worker:{studio.__version__}",
        "Wrong product/worker version",
    )
    worker = hashlib.sha256((runtime / "runner/node_checks.cjs").read_bytes()).hexdigest()
    if lane == "release-0.4.2":
        require(
            source == RELEASE_SOURCE and worker == RELEASE_WORKER_SHA256, "Published release baseline changed"
        )
    command = [execution.DOCKER, "image", "inspect", execution.IMAGE, "--format", "{{.Id}}"]
    image = subprocess.check_output(command, text=True).strip()  # noqa: S603 -- trusted broker-selected Docker executable.
    require(image.startswith("sha256:") and len(image) == 71, "Worker image identity missing")
    return {
        "lane": lane,
        "runtime_source": source,
        "runtime_version": studio.__version__,
        "worker_node_sha256": worker,
        "worker_image_id": image,
        "validation_source": os.environ.get("GITHUB_SHA"),
        "run_id": os.environ.get("GITHUB_RUN_ID"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "host": "GitHub-hosted Linux",
        "toolchain_caveat": "The image was freshly built from the identified source. Mutable upstream base tags/APT packages mean it is not asserted identical to a historical image.",
        "isolation": {
            "network": "none",
            "user": "65534:65534",
            "read_only": True,
            "memory_mib": 1024,
            "cpus": 2,
            "pids": 128,
        },
    }


async def toolchain_versions() -> dict:
    """Read actual tool versions inside the same restricted worker, with no packages/network."""
    commands = {
        "python": ["python", "--version"],
        "javascript": ["node", "--version"],
        "typescript": ["tsc", "--version"],
        "cpp": ["g++", "--version"],
        "c": ["gcc", "--version"],
        "java": ["javac", "-version"],
        "csharp": ["dotnet", "--version"],
        "rust": ["rustc", "--version"],
        "php": ["php", "--version"],
        "bash": ["bash", "--version"],
        "sql": ["sqlite3", "--version"],
        "assembly": ["as", "--version"],
    }
    program = (
        "import json,subprocess,sys\nsys.path.insert(0,'/opt')\nfrom worker import prepare_runtime\nprepare_runtime()\ncommands="
        + repr(commands)
        + "\nversions={}\nfor name,argv in commands.items():\n result=subprocess.run(argv,check=True,capture_output=True,text=True,timeout=10)\n versions[name]=(result.stdout or result.stderr).splitlines()[0]\nprint(json.dumps(versions))\n"
    )
    name = "code-flow-toolchain-" + uuid4().hex
    with tempfile.TemporaryDirectory(prefix="code-flow-toolchain-") as directory:
        root = Path(directory)
        (root / "job.json").write_text("{}", encoding="utf-8")
        argv = execution.container_arguments(root, name)
        argv.insert(-1, "--entrypoint=python")
        argv += ["-c", program]
        try:
            code, output = await execution.command(argv, timeout=90, output_limit=16384)
            require(code == 0, "Worker tool-version probe failed")
            versions = json.loads(output)
            require(
                isinstance(versions, dict) and set(versions) == set(LANGUAGES),
                "Incomplete real toolchain manifest",
            )
            require(
                all(isinstance(value, str) and 0 < len(value) <= 500 for value in versions.values()),
                "Invalid tool-version evidence",
            )
            return versions
        finally:
            await execution.command([execution.DOCKER, "rm", "--force", name], timeout=10, output_limit=4096)


def main() -> None:
    """Run the hosted acceptance suite and retain failed evidence without converting it to a pass."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-root", type=Path, required=True)
    parser.add_argument("--runtime-source", required=True)
    parser.add_argument("--lane", choices=["release-0.4.2", "current"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    evidence = Evidence(args.output.resolve(), provenance(args.runtime_root, args.runtime_source, args.lane))
    try:
        evidence.provenance["toolchain"] = asyncio.run(toolchain_versions())
        asyncio.run(broker_scenarios(evidence))
        asyncio.run(anchor_scenarios(evidence))
        private_scenarios(evidence)
        require(
            len(evidence.rows) == len(LANGUAGES) * 4 + len(SYNTAX_FAILURES) + len(SAMPLES),
            "Incomplete scenario matrix",
        )
        require(not evidence.errors, "Real compiler scenario failures: " + "; ".join(evidence.errors))
        evidence.provenance["acceptance"] = "passed"
        print(
            "COMPILER_ACCEPTANCE="
            + json.dumps(
                {
                    "lane": args.lane,
                    "runtime_source": args.runtime_source,
                    "languages": list(LANGUAGES),
                    "scenarios": len(evidence.rows),
                    "positive_cases_per_flow": sum(
                        len(practical_project(language).cases) for language in LANGUAGES
                    ),
                    "acceptance": "passed",
                }
            ),
            flush=True,
        )
    finally:
        evidence.save()


if __name__ == "__main__":
    main()
