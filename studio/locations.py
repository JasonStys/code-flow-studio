# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: tool_locations(result, project)@L24; process(record, stage, failed)@L62
# variables: LIMIT@L20; ANSI@L21; file@L26; sources@L26; name@L30; text@L30; name@L40; names@L40; path@L41; patterns@L42; details@L49; artifact@L55; name@L55; text@L55; findings@L57; unlocated@L58; seen@L59; truncated@L60; before@L65; stream@L66; output@L67; message@L68; pattern@L69; match@L70; name@L71; line@L77; column@L80; key@L85; truncated@L90; compilation@L115; case@L117; index@L117; generated@L119; fuzz@L121; finding@L122; index@L122; item@L127; line@L128; name@L128; truncated@L134
# parameters: project@L24; result@L24; failed@L62; record@L62; stage@L62
# </code-map>

"""Bounded tool-output location extraction by Jason Stys; messages remain untrusted text.

Locations refer only to supplied source snapshots or known generated harnesses.
Compiler/runtime output is evidence, not a proof of root cause. See docs/code-index.md.
"""

import hashlib
import re

from studio.models import Project

LIMIT = 1000
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def tool_locations(result: dict, project: Project) -> dict:
    """Extract validated file/line references from fixed adapters, keeping unmapped failures explicit."""
    sources = {file.name: (file.content, "source") for file in project.files if file.encoding == "text"}
    sources.update(
        {
            name: (text, "generated")
            for name, text in (
                ("test_generated.py", project.tests),
                (
                    "fuzz_harness.py" if project.fuzz_engine == "atheris" else "fuzz_harness.cpp",
                    project.fuzz_harness,
                ),
            )
            if text
        }
    )
    names = "|".join(re.escape(name) for name in sorted(sources, key=len, reverse=True))
    path = rf"(?<![\w./\\-])(?P<file>(?:(?:file://)?/tmp/project/|\./)?(?:{names}))"
    patterns = [
        re.compile(path + r":(?P<line>\d{1,9})(?!\d)(?::(?P<column>\d{1,9})(?!\d))?"),
        re.compile(path + r"\((?P<line>\d{1,9})(?:,(?P<column>\d{1,9}))?\)"),
        re.compile(r"File [\"']" + path + r"[\"'], line (?P<line>\d{1,9})(?!\d)"),
        re.compile(path + r": line (?P<line>\d{1,9})(?!\d)"),
        re.compile(path + r" on line (?P<line>\d{1,9})(?!\d)"),
    ]
    details = {
        name: {
            "lines": len(text.replace("\r\n", "\n").replace("\r", "\n").split("\n")),
            "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
            "artifact": artifact,
        }
        for name, (text, artifact) in sources.items()
    }
    findings = []
    unlocated = []
    seen = set()
    truncated = False

    def process(record: dict, stage: str, failed: bool = False) -> None:
        """Accept only bounded, in-range references; never infer a line from an exit code alone."""
        nonlocal truncated
        before = len(findings)
        for stream in ("stdout", "stderr"):
            output = ANSI.sub("", str(record.get(stream, ""))[-8192:])
            for message in output.splitlines():
                for pattern in patterns:
                    for match in pattern.finditer(message):
                        name = (
                            match["file"]
                            .removeprefix("file://")
                            .removeprefix("/tmp/project/")  # noqa: S108 -- normalize an in-memory container path, not a host temporary file
                            .removeprefix("./")
                        )
                        line = int(match["line"])
                        if not 0 < line <= details[name]["lines"]:
                            continue
                        column = (
                            int(match["column"])
                            if "column" in match.re.groupindex and match["column"]
                            else None
                        )
                        key = (stage, name, line, column, message[:500])
                        if key in seen:
                            continue
                        seen.add(key)
                        if len(findings) == LIMIT:
                            truncated = True
                            continue
                        findings.append(
                            {
                                "file": name,
                                "line": line,
                                "column": column,
                                "column_unit": "tool-reported",
                                "stage": stage,
                                "code": "TOOL-LOCATION",
                                "origin": "tool-output",
                                "severity": "error" if failed else "review",
                                "message": message[:500],
                                "source_sha256": details[name]["source_sha256"],
                                "artifact": details[name]["artifact"],
                            }
                        )
        if failed and before == len(findings):
            unlocated.append(
                {
                    "stage": stage,
                    "reason": "Failure has no recognized in-range source location; review raw evidence. No root-cause line inferred.",
                }
            )

    compilation = result.get("compilation", {})
    process(compilation, "compilation", compilation.get("exit_code", 0) != 0)
    for index, case in enumerate(result.get("checks", {}).get("cases", [])):
        process(case, f"case:{index}:{case.get('name', '')}", not case.get("passed", False))
    generated = result.get("generated_tests", {})
    process(generated, "generated-tests", generated.get("exit_code", 0) != 0)
    fuzz = result.get("fuzz", {})
    for index, finding in enumerate(fuzz.get("findings", [])):
        process(finding.get("process", {}), f"fuzz:{index}", True)
    process(fuzz.get("build", {}), "fuzz-build", fuzz.get("build", {}).get("exit_code", 0) != 0)
    process(fuzz.get("process", {}), "fuzz-process", fuzz.get("status") == "findings")
    # Treat worker JSON like untrusted logs: bind original paths, bounds and revision before display.
    for item in result.get("unused", {}).get("findings", [])[: LIMIT + 1]:
        name, line = item.get("file"), item.get("line")
        if name not in details or type(line) is not int or not 0 < line <= details[name]["lines"]:
            continue
        if item.get("source_sha256") != details[name]["source_sha256"]:
            continue
        if len(findings) >= LIMIT:
            truncated = True
            break
        findings.append(
            {**item, "stage": "unused-code", "artifact": "source", "column_unit": "tool-reported"}
        )
    return {
        "diagnostics": findings,
        "diagnostics_truncated": truncated,
        "unlocated_failures": unlocated,
        "location_caveat": "Tool-reported references, not proven root causes. Output may be incomplete, misleading or truncated; unrecognized paths remain in raw logs.",
    }
