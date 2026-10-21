# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L68
# functions: read_text(path)@L43; read_json(path)@L50; read_xml(path)@L55; __init__(self, project)@L71; name(self, path)@L90; line(self, name, value)@L95; add_lines(self, path, counts)@L100; finding(self, path, line, column, code, message)@L111; coverage(self, tool, metric, cases, expected)@L136; cobertura(evidence, path, case_index)@L190; jacoco(evidence, path)@L212; gcov(evidence, path)@L231; lcov(evidence, text)@L249; shell_lines(node)@L270; assembly_symbols(evidence)@L286; native_checks(project, work, execute, command)@L317; unused_checks(evidence, root, execute)@L335; measure(evidence, root, execute, command)@L560
# variables: MAX_REPORT@L24; SUFFIXES@L25; text@L59; text@L62; file@L75; name@L82; text@L82; name@L84; text@L84; value@L92; line@L97; name@L102; lines@L105; count@L106; value@L106; line@L107; name@L113; key@L116; files@L138; name@L139; text@L139; counts@L140; covered@L147; value@L147; count@L158; line@L158; count@L159; line@L159; budget@L165; key@L166; record@L167; values@L168; budget@L170; file@L172; measured@L172; complete@L173; case@L175; file@L185; item@L192; name@L193; line@L197; line@L199; condition@L200; file@L214; name@L215; line@L218; line@L226; stream@L233; text@L234; file@L237; name@L238; line@L241; line@L244; branch@L245; index@L245; name@L251; row@L252; name@L254; _@L256; count@L256; line@L256; block@L259; branch@L259; count@L259; line@L259; output@L272; position@L275; value@L278; item@L281; name@L288; text@L288; definitions@L289; exported@L290; used@L291; line@L292; source@L292; source@L293; label@L299; source@L302; source@L304; column@L306; label@L306; line@L306; evidence@L319; root@L320; unused@L322; coverage@L326; coverage@L328; project@L337; language@L338; entry@L339; output@L340; allowed@L341; result@L344; item@L349; tool@L353; result@L355; item@L371; location@L374; tool@L382; result@L384; line@L402; item@L403; code@L404; span@L406; tool@L415; allowed@L417; result@L418; file@L435; item@L436; tool@L444; allowed@L446; result@L447; file@L464; item@L465; tool@L467; allowed@L469; result@L470; item@L482; tool@L486; allowed@L488; result@L489; file@L504; item@L505; tool@L513; result@L515; line@L531; match@L532; tool@L537; result@L540; tool@L541; project@L562; entry@L563; language@L563; work@L564; build@L565; metric@L566; tool@L566; run@L567; metric@L569; tool@L569; build@L570; run@L580; metric@L582; tool@L582; build@L583; run@L598; metric@L600; tool@L600; classes@L601; build@L603; run@L604; metric@L613; tool@L613; build@L614; metric@L616; tool@L616; metric@L619; tool@L619; run@L620; metric@L622; tool@L622; build@L623; metric@L635; tool@L635; name@L636; tree@L637; result@L638; line@L645; metric@L647; tool@L647; result@L649; cases@L652; case@L653; index@L653; output@L654; environment@L655; run@L663; run@L665; run@L676; result@L691; lines@L703; name@L703; count@L704; line@L704; trace@L708; match@L709; current@L712; row@L713; current@L715; _@L717; hits@L717; line@L717; output@L720; result@L721; lines@L727; name@L727; note@L730; result@L731; file@L734; profiles@L737; result@L738; output@L751; result@L752; output@L767; result@L768; result@L789; row@L790; match@L791; name@L793; existing@L795
# parameters: path@L43; path@L50; path@L55; project@L71; self@L71; path@L90; self@L90; name@L95; self@L95; value@L95; counts@L100; path@L100; self@L100; code@L111; column@L111; line@L111; message@L111; path@L111; self@L111; cases@L136; expected@L136; metric@L136; self@L136; tool@L136; case_index@L190; evidence@L190; path@L190; evidence@L212; path@L212; evidence@L231; path@L231; evidence@L249; text@L249; node@L270; evidence@L286; command@L317; execute@L317; project@L317; work@L317; evidence@L335; execute@L335; root@L335; command@L560; evidence@L560; execute@L560; root@L560
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

    def finding(self, path, line, column, code, message) -> None:
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
                "severity": "review",
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
    for item in read_xml(path).iter("class"):
        name = evidence.name(item.get("filename", ""))
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
    if isinstance(node, dict):
        if node.get("Type") in {"CallExpr", "ArithmCmd", "TestClause", "DeclClause", "LetClause"}:
            position = node.get("Pos", {})
            if position.get("Line"):
                output.add(int(position["Line"]))
        for value in node.values():
            output.update(shell_lines(value))
    elif isinstance(node, list):
        for item in node:
            output.update(shell_lines(item))
    return output


def assembly_symbols(evidence: Evidence) -> None:
    """Review-only unreferenced named local labels; preserve exports, metadata and numeric labels."""
    for name, text in evidence.sources.items():
        definitions = {}
        exported = {"main", "_start"}
        used = set()
        for line, source in enumerate(text.splitlines(), 1):
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
    except (OSError, ValueError, KeyError, TypeError, ET.ParseError) as error:
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
    try:
        if language in {"javascript", "typescript"}:
            result = execute(
                ["node", "/opt/node_checks.cjs", "lint", "/input/job.json", str(output)], timeout=20
            )
            if result["exit_code"] != 0:
                raise ValueError(result["stderr"])
            for item in read_json(output)["findings"]:
                evidence.finding(
                    item["file"], item["line"], item.get("column"), item["code"], item["message"]
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
            for file in read_json(output).get("files", []):
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
            for file in read_json(output).get("files", []):
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
            "status": "completed"
            if result["exit_code"] in allowed and not result.get("timeout")
            else "blocked",
            "tool": tool,
            "process": result,
            "findings": evidence.findings,
            "findings_truncated": evidence.findings_truncated,
            "scope": "Review-only language-native unused candidates; public APIs, side effects and dynamic references require human review.",
        }
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {
            "status": "blocked",
            "reason": f"Unused checks unavailable: {type(error).__name__}: {str(error)[:300]}",
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
                "quiet",
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
