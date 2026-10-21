# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L68
# functions: read_text(path)@L43; read_json(path)@L50; read_xml(path)@L55; __init__(self, project)@L71; name(self, path)@L90; line(self, name, value)@L95; add_lines(self, path, counts)@L100; finding(self, path, line, column, code, message, severity)@L111; coverage(self, tool, metric, cases, expected)@L136; cobertura(evidence, path, case_index)@L190; jacoco(evidence, path)@L216; gcov(evidence, path)@L235; lcov(evidence, text)@L253; shell_lines(node)@L274; assembly_symbols(evidence)@L291; native_checks(project, work, execute, command)@L322; unused_checks(evidence, root, execute)@L340; measure(evidence, root, execute, command)@L585
# variables: MAX_REPORT@L24; SUFFIXES@L25; text@L59; text@L62; file@L75; name@L82; text@L82; name@L84; text@L84; value@L92; line@L97; name@L102; lines@L105; count@L106; value@L106; line@L107; name@L113; key@L116; files@L138; name@L139; text@L139; counts@L140; covered@L147; value@L147; count@L158; line@L158; count@L159; line@L159; budget@L165; key@L166; record@L167; values@L168; budget@L170; file@L172; measured@L172; complete@L173; case@L175; file@L185; document@L192; roots@L193; source@L193; item@L194; reported@L195; paths@L196; root@L196; candidate@L197; name@L197; path@L197; line@L201; line@L203; condition@L204; file@L218; name@L219; line@L222; line@L230; stream@L237; text@L238; file@L241; name@L242; line@L245; line@L248; branch@L249; index@L249; name@L255; row@L256; name@L258; _@L260; count@L260; line@L260; block@L263; branch@L263; count@L263; line@L263; output@L276; pending@L277; item@L279; position@L282; name@L293; text@L293; definitions@L294; exported@L295; used@L296; line@L297; source@L297; source@L298; label@L304; source@L307; source@L309; column@L311; label@L311; line@L311; evidence@L324; root@L325; unused@L327; coverage@L331; coverage@L333; project@L342; language@L343; entry@L344; output@L345; allowed@L346; result@L347; parse_failed@L348; result@L351; item@L356; parse_failed@L357; tool@L366; result@L368; item@L384; location@L387; tool@L395; result@L397; line@L415; item@L416; code@L417; span@L419; tool@L428; allowed@L430; result@L431; parsed@L448; parse_failed@L449; file@L450; item@L451; tool@L459; allowed@L461; result@L462; parsed@L479; parse_failed@L480; file@L481; item@L482; tool@L484; allowed@L486; result@L487; item@L499; parse_failed@L500; tool@L504; allowed@L506; result@L507; file@L524; item@L525; parse_failed@L526; tool@L534; result@L536; line@L552; match@L553; tool@L558; result@L561; tool@L562; project@L587; entry@L588; language@L588; work@L589; build@L590; metric@L591; tool@L591; run@L592; metric@L594; tool@L594; build@L595; run@L605; metric@L607; tool@L607; build@L608; run@L623; metric@L625; tool@L625; classes@L626; build@L628; run@L629; metric@L638; tool@L638; build@L639; metric@L641; tool@L641; metric@L644; tool@L644; run@L645; metric@L647; tool@L647; build@L648; metric@L660; tool@L660; name@L661; tree@L662; result@L663; line@L670; metric@L672; tool@L672; result@L674; cases@L677; case@L678; index@L678; output@L679; environment@L680; run@L688; run@L690; run@L701; result@L716; lines@L730; name@L730; count@L731; line@L731; trace@L735; match@L736; current@L739; row@L740; current@L742; _@L744; hits@L744; line@L744; output@L747; result@L748; lines@L754; name@L754; note@L757; result@L758; file@L761; profiles@L764; result@L765; output@L778; result@L779; output@L794; result@L795; result@L816; row@L817; match@L818; name@L820; existing@L822
# parameters: path@L43; path@L50; path@L55; project@L71; self@L71; path@L90; self@L90; name@L95; self@L95; value@L95; counts@L100; path@L100; self@L100; code@L111; column@L111; line@L111; message@L111; path@L111; self@L111; severity@L111; cases@L136; expected@L136; metric@L136; self@L136; tool@L136; case_index@L190; evidence@L190; path@L190; evidence@L216; path@L216; evidence@L235; path@L235; evidence@L253; text@L253; node@L274; evidence@L291; command@L322; execute@L322; project@L322; work@L322; evidence@L340; execute@L340; root@L340; command@L585; evidence@L585; execute@L585; root@L585
# </code-map>

"""Jason Stys: real polyglot coverage and unused-code adapters, container execution only.

Pure parsers can be imported by controller tests; submitted sources are never imported.
Execution is supplied by the restricted worker. Symbol/variable map: docs/code-index.md.
"""

import gzip
import hashlib
import json
import posixpath
import re
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_REPORT = 8 * 1024 * 1024
SUFFIXES = {
    "javascript": (".js",),
    "typescript": (".ts",),
    "cpp": (".cpp", ".cc", ".h", ".hpp"),
    "c": (".c", ".h"),
    "java": (".java",),
    "csharp": (".cs",),
    "rust": (".rs",),
    "php": (".php",),
    "bash": (".sh",),
    "sql": (".sql",),
    "assembly": (
        ".S",
        ".s",
    ),
}


def read_text(path: Path):
    """Bound all native report reads, including traces containing private transient expansions."""
    if path.stat().st_size > MAX_REPORT:
        raise ValueError("Tool report exceeds eight MiB")
    return path.read_text(encoding="utf-8", errors="replace")


def read_json(path: Path):
    """Read bounded tool reports, never an arbitrary tool-reported path."""
    return json.loads(read_text(path))


def read_xml(path: Path):
    """Reject DTDs and non-UTF-8 XML before parsing bounded tool output."""
    if path.stat().st_size > MAX_REPORT:
        raise ValueError("Tool report exceeds eight MiB")
    text = path.read_text(encoding="utf-8")
    if "<!DOCTYPE" in text.upper():
        # JaCoCo's fixed external declaration is unnecessary and is never fetched.
        text = re.sub(r'<!DOCTYPE report PUBLIC "[^"<>]*" "report\.dtd">', "", text)
        if "<!DOCTYPE" in text.upper():
            raise ValueError("XML DTDs are not accepted")
    return ET.fromstring(text)  # noqa: S314 -- bounded UTF-8 input with DTD declarations rejected


class Evidence:
    """Bind adapter locations to original flat files; aggregate observed counts without invented lines."""

    def __init__(self, project: dict):
        self.project = project
        self.sources = {
            file["name"]: file["content"]
            for file in project["files"]
            if file["encoding"] == "text"
            and (file["name"].endswith(SUFFIXES[project["language"]]) or file["name"] == project["entry"])
        }
        self.counts = {}
        self.line_counts = {
            name: len(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
            for name, text in self.sources.items()
        }
        self.hashes = {name: hashlib.sha256(text.encode()).hexdigest() for name, text in self.sources.items()}
        self.branches = {}
        self.findings = []
        self.finding_keys = set()
        self.findings_truncated = False

    def name(self, path: str) -> str | None:
        """Accept original basenames or normalized paths within this worker's project, not arbitrary suffixes."""
        value = posixpath.normpath(str(path).replace("\\", "/")).removeprefix("/tmp/project/")  # noqa: S108 -- normalize an inert private worker path, never host /tmp
        return value if value in self.sources else None

    def line(self, name: str, value) -> int | None:
        """Retain only real one-based physical source lines (including an EOF anchor)."""
        line = int(value)
        return line if 0 < line <= self.line_counts[name] else None

    def add_lines(self, path: str, counts: dict) -> None:
        """Union measurements across approved cases, retaining zero-count executable lines."""
        name = self.name(path)
        if name is None:
            return
        lines = self.counts.setdefault(name, {})
        for value, count in counts.items():
            line = self.line(name, value)
            if line is not None:
                lines[line] = max(lines.get(line, 0), max(0, int(count)))

    def finding(self, path, line, column, code, message, severity="review") -> None:
        """Bound and bind native lint candidates; source hashes identify the analyzed revision."""
        name = self.name(path)
        if name is None or line is None or self.line(name, line) is None:
            return
        key = (name, int(line), column, str(code), str(message))
        if key in self.finding_keys:
            return
        if len(self.findings) >= 1000:
            self.findings_truncated = True
            return
        self.finding_keys.add(key)
        self.findings.append(
            {
                "file": name,
                "line": int(line),
                "column": int(column) if column else None,
                "code": str(code)[:100],
                "message": str(message)[:500],
                "severity": severity,
                "origin": "native-unused",
                "source_sha256": self.hashes[name],
            }
        )

    def coverage(self, tool: str, metric: str, cases: list[dict], expected: int) -> dict:
        """Produce explicit per-file coverage, including unknown records and a shared location budget."""
        files = {}
        for name, text in self.sources.items():
            counts = self.counts.get(name)
            if not counts:
                files[name] = {
                    "status": "not-measured",
                    "reason": "Tool reported no executable locations; not assumed fully covered",
                }
                continue
            covered = sum(value > 0 for value in counts.values())
            files[name] = {
                "status": "measured",
                "metric": metric,
                "summary": {
                    "covered_lines": covered,
                    "num_statements": len(counts),
                    "missing_lines": len(counts) - covered,
                    "percent_covered": 100 * covered / len(counts),
                },
                "source_sha256": hashlib.sha256(text.encode()).hexdigest(),
                "missing_lines": sorted(line for line, count in counts.items() if not count),
                "executed_lines": sorted(line for line, count in counts.items() if count),
                "excluded_lines": [],
                "missing_branches": [],
                "branch_points": self.branches.get(name, []),
                "truncated": False,
            }
        budget = 20000
        for key in ("missing_lines", "branch_points", "executed_lines", "excluded_lines"):
            for record in files.values():
                values = record.get(key, [])
                record[key] = values[:budget]
                budget -= len(record[key])
                record["truncated"] = record.get("truncated", False) or len(values) != len(record[key])
        measured = any(file["status"] == "measured" for file in files.values())
        complete = len(cases) == expected and all(
            not case.get("timeout") and case.get("exit_code") == case.get("expected_exit_code", 0)
            for case in cases
        )
        return {
            "status": "measured" if measured and complete else "partial" if measured else "blocked",
            "tool": tool,
            "metric": metric,
            "files": files,
            "entry": files.get(self.project["entry"], {}).get("summary", {}),
            "cases": cases,
            "requested_cases": expected,
            "locations_truncated": any(file.get("truncated") for file in files.values()),
            "scope": "Instrumented approved CLI reruns only, separate from timing/RSS and generated pytest tests. Unknown/unloaded sources remain not-measured. Branch points retain tool IDs, not invented destination lines. Shared-worker interference remains possible.",
        }


def cobertura(evidence: Evidence, path: Path, case_index=None) -> None:
    """Read real Coverlet/compatible XML line hits and per-line condition ratios."""
    document = read_xml(path)
    roots = [source.text or "" for source in document.findall("./sources/source")]
    for item in document.iter("class"):
        reported = item.get("filename", "")
        paths = [posixpath.join(root, reported) for root in roots] if roots else [reported]
        name = next((candidate for path in paths if (candidate := evidence.name(path))), None)
        if name is None:
            continue
        evidence.add_lines(
            name, {line.attrib["number"]: line.get("hits", "0") for line in item.findall("./lines/line")}
        )
        for line in item.findall("./lines/line"):
            for condition in line.findall("./conditions/condition"):
                evidence.branches.setdefault(name, []).append(
                    {
                        "line": int(line.attrib["number"]),
                        "branch_id": condition.get("number"),
                        "case_index": case_index,
                        "coverage": condition.get("coverage"),
                        "kind": "coverlet-condition",
                    }
                )


def jacoco(evidence: Evidence, path: Path) -> None:
    """JaCoCo instruction-backed source lines; branch counts are not source-to-source arcs."""
    for file in read_xml(path).iter("sourcefile"):
        name = evidence.name(file.get("name", ""))
        if name is None:
            continue
        evidence.add_lines(name, {line.attrib["nr"]: line.get("ci", "0") for line in file.findall("line")})
        evidence.branches[name] = [
            {
                "line": int(line.attrib["nr"]),
                "missing": int(line.get("mb", 0)),
                "covered": int(line.get("cb", 0)),
                "kind": "jacoco-branch-count",
            }
            for line in file.findall("line")
            if int(line.get("mb", 0)) + int(line.get("cb", 0))
        ]


def gcov(evidence: Evidence, path: Path) -> None:
    """Parse gzip-compressed GCC JSON; no shell or approximate source scanning."""
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        text = stream.read(MAX_REPORT + 1)
    if len(text) > MAX_REPORT:
        raise ValueError("GCC report exceeds eight MiB")
    for file in json.loads(text).get("files", []):
        name = evidence.name(file["file"])
        if name is None:
            continue
        evidence.add_lines(name, {line["line_number"]: line["count"] for line in file["lines"]})
        evidence.branches[name] = [
            {"line": line["line_number"], "branch_id": index, "hits": branch["count"], "kind": "gcov-branch"}
            for line in file["lines"]
            for index, branch in enumerate(line.get("branches", []))
        ]


def lcov(evidence: Evidence, text: str) -> None:
    """LLVM lcov source counts preserve macro/compiler line mappings and branch IDs."""
    name = None
    for row in text.splitlines():
        if row.startswith("SF:"):
            name = evidence.name(row[3:])
        elif name and row.startswith("DA:"):
            line, count, *_ = row[3:].split(",")
            evidence.add_lines(name, {line: count})
        elif name and row.startswith("BRDA:"):
            line, block, branch, count = row[5:].split(",")
            evidence.branches.setdefault(name, []).append(
                {
                    "line": int(line),
                    "branch_id": f"{block}:{branch}",
                    "hits": int(count) if count != "-" else 0,
                    "kind": "llvm-branch",
                }
            )


def shell_lines(node) -> set[int]:
    """Extract command-entry lines from shfmt's real Bash AST, not blank/comment heuristics."""
    output = set()
    pending = [node]
    while pending:
        item = pending.pop()
        if isinstance(item, dict):
            if item.get("Type") in {"CallExpr", "ArithmCmd", "TestClause", "DeclClause", "LetClause"}:
                position = item.get("Pos", {})
                if position.get("Line"):
                    output.add(int(position["Line"]))
            pending.extend(item.values())
        elif isinstance(item, list):
            pending.extend(item)
    return output


def assembly_symbols(evidence: Evidence) -> None:
    """Review-only unreferenced named local labels; preserve exports, metadata and numeric labels."""
    for name, text in evidence.sources.items():
        definitions = {}
        exported = {"main", "_start"}
        used = set()
        for line, source in enumerate(text.replace("\r\n", "\n").replace("\r", "\n").split("\n"), 1):
            source = source.split("#", 1)[0]
            if re.match(r"\s*\.(?:global|globl|weak|extern)\b", source):
                exported.update(re.findall(r"[A-Za-z_.$][\w.$]*", source)[1:])
                continue
            if re.match(r"\s*\.(?:type|size|file|loc|section)\b", source):
                continue
            label = re.match(r"\s*([A-Za-z_.$][\w.$]*):", source)
            if label:
                definitions[label[1]] = (line, label.start(1) + 1)
                source = source[label.end() :]
            # String/data literal contents do not constitute symbol references.
            source = re.sub(r'"(?:[^"\\]|\\.)*"', "", source)
            used.update(re.findall(r"[A-Za-z_.$][\w.$]*", source))
        for label, (line, column) in definitions.items():
            if label not in used and label not in exported:
                evidence.finding(
                    name,
                    line,
                    column,
                    "ASM-UNREFERENCED-LABEL",
                    f"Possibly unreferenced local label '{label}'; fall-through/dynamic linkage may be intentional",
                )


def native_checks(project: dict, work: Path, execute, command: list[str]) -> tuple[dict, dict]:
    """Run fixed native tools in the existing container; failures remain blocked, never fake measurements."""
    evidence = Evidence(project)
    root = work / ".analysis"
    root.mkdir()
    unused = unused_checks(evidence, root, execute)
    if not project["cases"]:
        return {"status": "not-applicable", "reason": "Approved CLI cases required"}, unused
    try:
        coverage = measure(evidence, root, execute, command)
    except (OSError, ValueError, KeyError, TypeError, RecursionError, ET.ParseError) as error:
        coverage = {
            "status": "blocked",
            "reason": f"Native coverage unavailable: {type(error).__name__}: {str(error)[:300]}",
        }
    return coverage, unused


def unused_checks(evidence: Evidence, root: Path, execute) -> dict:
    """Native/compiler unused candidates, not whole-program proof or host-side target execution."""
    project = evidence.project
    language = project["language"]
    entry = project["entry"]
    output = root / "unused.json"
    allowed = {0}
    result = {"exit_code": None, "stderr": "Tool not started"}
    parse_failed = False
    try:
        if language in {"javascript", "typescript"}:
            result = execute(
                ["node", "/opt/node_checks.cjs", "lint", "/input/job.json", str(output)], timeout=20
            )
            if result["exit_code"] != 0:
                raise ValueError(result["stderr"])
            for item in read_json(output)["findings"]:
                parse_failed |= item["code"] == "parse-error"
                evidence.finding(
                    item["file"],
                    item["line"],
                    item.get("column"),
                    item["code"],
                    item["message"],
                    item.get("severity", "review"),
                )
            tool = "ESLint/@typescript-eslint"
        elif language in {"c", "cpp"}:
            result = execute(
                [
                    "gcc" if language == "c" else "g++",
                    "-c",
                    "-std=c17" if language == "c" else "-std=c++20",
                    "-Wall",
                    "-Wextra",
                    "-Wunused",
                    "-fdiagnostics-format=json",
                    entry,
                    "-o",
                    str(root / "unused.o"),
                ],
                timeout=25,
                stderr_path=output,
            )
            for item in read_json(output):
                if "unused" not in item.get("option", ""):
                    continue
                location = item["locations"][0]["caret"]
                evidence.finding(
                    location["file"],
                    location["line"],
                    location.get("column"),
                    item["option"],
                    item["message"],
                )
            tool = "GCC unused diagnostics"
        elif language == "rust":
            result = execute(
                [
                    "rustc",
                    "--edition",
                    "2021",
                    "--emit=metadata",
                    "--error-format=json",
                    "-W",
                    "unused",
                    "-W",
                    "dead_code",
                    entry,
                    "--out-dir",
                    str(root),
                ],
                timeout=25,
                stderr_path=output,
            )
            for line in read_text(output).splitlines():
                item = json.loads(line)
                code = (item.get("code") or {}).get("code", "")
                if code == "dead_code" or code.startswith("unused"):
                    for span in item.get("spans", []):
                        if span.get("is_primary"):
                            evidence.finding(
                                span["file_name"],
                                span["line_start"],
                                span["column_start"],
                                code,
                                item["message"],
                            )
            tool = "rustc unused/dead_code lints"
        elif language == "java":
            allowed = {0, 4}
            result = execute(
                [
                    "/opt/pmd-bin-7.28.0/bin/pmd",
                    "check",
                    "--no-cache",
                    "--no-progress",
                    "--format",
                    "json",
                    "--rulesets",
                    "/opt/java-unused.xml",
                    "--report-file",
                    str(output),
                    "--dir",
                    ",".join(evidence.sources),
                ],
                timeout=35,
            )
            parsed = read_json(output)
            parse_failed = bool(parsed.get("processingErrors"))
            for file in parsed.get("files", []):
                for item in file.get("violations", []):
                    evidence.finding(
                        file["filename"],
                        item["beginline"],
                        item.get("begincolumn"),
                        item["rule"],
                        item["description"],
                    )
            tool = "PMD unused declarations"
        elif language == "php":
            allowed = {0, 2}
            result = execute(
                [
                    "php",
                    "/opt/phpmd.phar",
                    "analyze",
                    "--format",
                    "json",
                    "--ruleset",
                    "phar:///opt/phpmd.phar/rulesets/unusedcode.xml",
                    "--no-cache",
                    "--threads",
                    "1",
                    *evidence.sources,
                ],
                timeout=25,
                stdout_path=output,
            )
            parsed = read_json(output)
            parse_failed = bool(parsed.get("errors"))
            for file in parsed.get("files", []):
                for item in file.get("violations", []):
                    evidence.finding(file["file"], item["beginLine"], None, item["rule"], item["description"])
            tool = "PHPMD unusedcode"
        elif language == "bash":
            allowed = {0, 1}
            result = execute(
                [
                    "shellcheck",
                    "--norc",
                    "--format=json",
                    "--shell=bash",
                    "--include=2034,2317,2329",
                    *evidence.sources,
                ],
                timeout=15,
                stdout_path=output,
            )
            for item in read_json(output):
                parse_failed |= item["code"] not in {2034, 2317, 2329}
                evidence.finding(
                    item["file"], item["line"], item["column"], "SC" + str(item["code"]), item["message"]
                )
            tool = "ShellCheck unused/unreachable rules"
        elif language == "sql":
            allowed = {0, 1}
            result = execute(
                [
                    "sqlfluff",
                    "lint",
                    "--ignore-local-config",
                    "--dialect",
                    "sqlite",
                    "--templater",
                    "raw",
                    "--rules",
                    "ST03,AL05",
                    "--format=json",
                    *evidence.sources,
                ],
                timeout=25,
                stdout_path=output,
            )
            for file in read_json(output):
                for item in file.get("violations", []):
                    parse_failed |= item["code"] not in {"ST03", "AL05"}
                    evidence.finding(
                        file["filepath"],
                        item.get("start_line_no", item.get("line_no")),
                        item.get("start_line_pos", item.get("line_pos")),
                        item["code"],
                        item["description"],
                    )
            tool = "SQLFluff unused CTE/table aliases"
        elif language == "csharp":
            result = execute(
                [
                    "dotnet",
                    "build",
                    "App.csproj",
                    "--no-incremental",
                    "--nologo",
                    "--verbosity",
                    "quiet",
                    "--ignore-failed-sources",
                    "-o",
                    str(root / "csharp-lint"),
                ],
                timeout=35,
                stdout_path=output,
            )
            for line in read_text(output).splitlines():
                match = re.search(
                    r"([^\s()]+\.cs)\((\d+),(\d+)\): warning (CS0168|CS0169|CS0219|CS0414): (.+?) \[", line
                )
                if match:
                    evidence.finding(match[1], match[2], match[3], match[4], match[5])
            tool = "C# compiler unused locals/private fields"
        else:
            assembly_symbols(evidence)
            result = {"exit_code": 0}
            tool = "GNU assembly local-symbol reference candidates"
        return {
            "status": ("partial" if parse_failed else "completed")
            if result["exit_code"] in allowed and not result.get("timeout")
            else "blocked",
            "reason": "A source file could not be fully parsed; review native evidence"
            if parse_failed
            else None,
            "tool": tool,
            "process": result,
            "findings": evidence.findings,
            "findings_truncated": evidence.findings_truncated,
            "scope": "Review-only language-native unused candidates; public APIs, side effects and dynamic references require human review.",
        }
    except (OSError, ValueError, KeyError, TypeError, RecursionError) as error:
        return {
            "status": "blocked",
            "reason": f"Unused checks unavailable: {type(error).__name__}: {str(error)[:300]}",
            "process": result,
            "findings": evidence.findings,
        }


def measure(evidence: Evidence, root: Path, execute, command: list[str]) -> dict:
    """Build/run instrumentation separately from baseline benchmarks and retain native measurement semantics."""
    project = evidence.project
    language, entry = project["language"], project["entry"]
    work = root.parent
    build = None
    tool = metric = ""
    run = command
    if language in {"c", "cpp"}:
        tool, metric = "GCC/gcov JSON", "gcov-executable-line"
        build = [
            "gcc" if language == "c" else "g++",
            "-std=c17" if language == "c" else "-std=c++20",
            "--coverage",
            "-O0",
            "-g",
            entry,
            "-o",
            str(root / "target"),
        ]
        run = [str(root / "target")]
    elif language == "rust":
        tool, metric = "rustc 1.99.1/matching LLVM lcov", "llvm-source-region-line"
        build = [
            "rustc",
            "--edition",
            "2021",
            "-C",
            "instrument-coverage",
            "-C",
            "link-dead-code",
            "-C",
            "opt-level=0",
            "-g",
            entry,
            "-o",
            str(root / "target"),
        ]
        run = [str(root / "target")]
    elif language == "java":
        tool, metric = "JaCoCo 0.8.15", "jacoco-instruction-backed-line"
        classes = root / "classes"
        classes.mkdir()
        build = ["javac", "-g", "-d", str(classes), entry]
        run = [
            "java",
            "-XX:MaxRAMPercentage=50",
            f"-javaagent:/opt/jacoco/lib/jacocoagent.jar=destfile={root / 'jacoco.exec'},append=true",
            "-cp",
            str(classes),
            Path(entry).stem,
        ]
    elif language == "assembly":
        tool, metric = "DWARF/Valgrind Callgrind", "instruction-backed-assembly-line"
        build = ["gcc", "-g", "-no-pie", entry, "-o", str(root / "target")]
    elif language in {"javascript", "typescript"}:
        tool, metric = "Node V8/v8-to-Istanbul", "v8-block-derived-line"
        (root / "v8").mkdir()
    elif language == "php":
        tool, metric = "PHP Xdebug", "php-opcode-line"
        run = ["php", "-d", "xdebug.mode=coverage", "-d", "auto_prepend_file=/opt/php_coverage.php", entry]
    elif language == "csharp":
        tool, metric = "Coverlet 8.0.1", "portable-pdb-sequence-point-line"
        build = [
            "dotnet",
            "build",
            "App.csproj",
            "--nologo",
            "--verbosity",
            "quiet",
            "--ignore-failed-sources",
            "-o",
            str(root / "csharp"),
        ]
    elif language == "bash":
        tool, metric = "shfmt Bash AST + Bash xtrace", "bash-command-entry-line"
        for name in evidence.sources:
            tree = root / (name + ".ast.json")
            result = execute(
                ["shfmt", "-ln", "bash", "-tojson", "-filename", name],
                evidence.sources[name],
                stdout_path=tree,
            )
            if result["exit_code"] != 0:
                raise ValueError("Bash AST extraction failed: " + result["stderr"])
            evidence.add_lines(name, {line: 0 for line in shell_lines(read_json(tree))})
    elif language == "sql":
        tool, metric = "SQLite complete_statement/execute", "sql-top-level-statement-start"
    if build:
        result = execute(build, timeout=45)
        if result["exit_code"] != 0:
            raise ValueError("Coverage build failed: " + result["stderr"] + result["stdout"])
    cases = []
    for index, case in enumerate(project["cases"]):
        output = root / f"case-{index}.json"
        environment = {}
        if language in {"javascript", "typescript"}:
            environment["NODE_V8_COVERAGE"] = str(root / "v8")
        elif language == "rust":
            environment["LLVM_PROFILE_FILE"] = str(root / "rust-%p-%m.profraw")
        elif language in {"php", "sql"}:
            environment["CFS_COVERAGE_OUTPUT"] = str(output)
        elif language == "bash":
            run = ["bash", "/opt/bash_coverage.sh", str(output), entry]
        elif language == "assembly":
            run = [
                "valgrind",
                "--tool=callgrind",
                "--dump-line=yes",
                "--dump-instr=no",
                "--compress-pos=no",
                "--compress-strings=no",
                "--callgrind-out-file=" + str(output),
                str(root / "target"),
            ]
        elif language == "csharp":
            run = [
                "/opt/coverlet/coverlet",
                str(root / "csharp/App.dll"),
                "--target",
                "/usr/share/dotnet/dotnet",
                "--targetargs",
                str(root / "csharp/App.dll"),
                "--format",
                "cobertura",
                "--include-test-assembly",
                "--output",
                str(output),
                "--verbosity",
                "normal",
            ]
        result = execute(run, case["stdin"], timeout=20, env=environment)
        cases.append(
            {
                "name": case["name"],
                "exit_code": result["exit_code"],
                "expected_exit_code": case["exit_code"],
                "timeout": result.get("timeout", False),
            }
        )
        if language == "csharp":
            cases[-1]["collector_messages"] = (result["stdout"] + result["stderr"])[-2000:]
        if result.get("timeout") or result["exit_code"] is None:
            break
        if language in {"php", "sql"}:
            for name, lines in read_json(output).items():
                evidence.add_lines(name, {line: count for line, count in lines.items() if int(count) >= -1})
        elif language == "csharp":
            cobertura(evidence, output if output.exists() else output.with_suffix(".cobertura.xml"), index)
        elif language == "bash":
            trace = read_text(output)
            for match in re.finditer(r"\x1e([^\x1e\x1f\r\n]+):(\d+)\x1f", trace):
                evidence.add_lines(match[1], {match[2]: 1})
        elif language == "assembly":
            current = None
            for row in read_text(output).splitlines():
                if row.startswith("fl="):
                    current = evidence.name(row[3:])
                elif current and re.match(r"^\d+ \d+", row):
                    line, hits, *_ = row.split()
                    evidence.add_lines(current, {line: hits})
    if language in {"javascript", "typescript"}:
        output = root / "node-coverage.json"
        result = execute(
            ["node", "/opt/node_checks.cjs", "coverage", "/input/job.json", str(output), str(root / "v8")],
            timeout=25,
        )
        if result["exit_code"] != 0:
            raise ValueError(result["stderr"])
        for name, lines in read_json(output).items():
            evidence.add_lines(name, lines)
    elif language in {"c", "cpp"}:
        for note in root.glob("*.gcno"):
            result = execute(["gcov", "--json-format", "--branch-probabilities", str(note)], timeout=15)
            if result["exit_code"] != 0:
                raise ValueError(result["stderr"])
        for file in work.glob("*.gcov.json.gz"):
            gcov(evidence, file)
    elif language == "rust":
        profiles = list(root.glob("*.profraw"))
        result = execute(
            [
                "rust-llvm-profdata",
                "merge",
                "-sparse",
                *map(str, profiles),
                "-o",
                str(root / "rust.profdata"),
            ],
            timeout=15,
        )
        if result["exit_code"] != 0:
            raise ValueError(result["stderr"])
        output = root / "rust.lcov"
        result = execute(
            [
                "rust-llvm-cov",
                "export",
                "-format=lcov",
                "-instr-profile=" + str(root / "rust.profdata"),
                str(root / "target"),
            ],
            stdout_path=output,
            timeout=15,
        )
        if result["exit_code"] != 0:
            raise ValueError(result["stderr"])
        lcov(evidence, read_text(output))
    elif language == "java":
        output = root / "jacoco.xml"
        result = execute(
            [
                "java",
                "-jar",
                "/opt/jacoco/lib/jacococli.jar",
                "report",
                str(root / "jacoco.exec"),
                "--classfiles",
                str(root / "classes"),
                "--sourcefiles",
                str(work),
                "--xml",
                str(output),
                "--quiet",
            ],
            timeout=20,
        )
        if result["exit_code"] != 0:
            raise ValueError(result["stderr"])
        jacoco(evidence, output)
    elif language == "assembly":
        result = execute(["objdump", "--dwarf=decodedline", str(root / "target")])
        for row in result["stdout"].splitlines():
            match = re.match(r"\s*(\S+)\s+(\d+)\s+0x[0-9a-f]+", row)
            if match:
                name = evidence.name(match[1])
                if name:
                    existing = evidence.counts.get(name, {}).get(int(match[2]), 0)
                    evidence.add_lines(name, {match[2]: existing})
    return evidence.coverage(tool, metric, cases, len(project["cases"]))
