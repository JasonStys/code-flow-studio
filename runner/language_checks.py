# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Evidence@L68
# functions: read_text(path)@L43; read_json(path)@L50; read_xml(path)@L55; __init__(self, project)@L71; name(self, path)@L89; line(self, name, value)@L94; add_lines(self, path, counts)@L99; finding(self, path, line, column, code, message)@L110; coverage(self, tool, metric, cases, expected)@L131; cobertura(evidence, path)@L185; jacoco(evidence, path)@L206; gcov(evidence, path)@L225; lcov(evidence, text)@L243; shell_lines(node)@L264; assembly_symbols(evidence)@L280; native_checks(project, work, execute, command)@L311; unused_checks(evidence, root, execute)@L329; measure(evidence, root, execute, command)@L539
# variables: MAX_REPORT@L24; SUFFIXES@L25; text@L59; text@L62; file@L75; name@L82; text@L82; name@L84; text@L84; value@L91; line@L96; name@L101; lines@L104; count@L105; value@L105; line@L106; name@L112; files@L133; name@L134; text@L134; counts@L135; covered@L142; value@L142; count@L153; line@L153; count@L154; line@L154; budget@L160; key@L161; record@L162; values@L163; budget@L165; file@L167; measured@L167; complete@L168; case@L170; file@L180; item@L187; name@L188; line@L192; line@L194; condition@L195; file@L208; name@L209; line@L212; line@L220; stream@L227; text@L228; file@L231; name@L232; line@L235; line@L238; branch@L239; index@L239; name@L245; row@L246; name@L248; _@L250; count@L250; line@L250; block@L253; branch@L253; count@L253; line@L253; output@L266; position@L269; value@L272; item@L275; name@L282; text@L282; definitions@L283; exported@L284; used@L285; line@L286; source@L286; source@L287; label@L293; source@L296; source@L298; column@L300; label@L300; line@L300; evidence@L313; root@L314; unused@L316; coverage@L320; coverage@L322; project@L331; language@L332; entry@L333; output@L334; allowed@L335; result@L338; item@L343; tool@L347; result@L349; item@L362; location@L365; tool@L373; result@L375; line@L393; item@L394; code@L395; span@L397; tool@L406; allowed@L408; result@L409; file@L426; item@L427; tool@L435; allowed@L437; result@L438; file@L443; item@L444; tool@L446; allowed@L448; result@L449; item@L461; tool@L465; allowed@L467; result@L468; file@L483; item@L484; tool@L492; result@L494; line@L510; match@L511; tool@L516; result@L519; tool@L520; project@L541; entry@L542; language@L542; work@L543; build@L544; metric@L545; tool@L545; run@L546; metric@L548; tool@L548; build@L549; run@L559; metric@L561; tool@L561; build@L562; run@L577; metric@L579; tool@L579; classes@L580; build@L582; run@L583; metric@L592; tool@L592; build@L593; metric@L595; tool@L595; metric@L598; tool@L598; run@L599; metric@L601; tool@L601; build@L602; metric@L614; tool@L614; name@L615; tree@L616; result@L617; line@L624; metric@L626; tool@L626; result@L628; cases@L631; case@L632; index@L632; output@L633; environment@L634; run@L642; run@L644; run@L655; result@L669; lines@L681; name@L681; count@L682; line@L682; trace@L686; match@L687; current@L690; row@L691; current@L693; _@L695; hits@L695; line@L695; output@L698; result@L699; lines@L705; name@L705; note@L708; result@L709; file@L712; profiles@L715; result@L716; output@L722; result@L723; output@L738; result@L739; result@L760; row@L761; match@L762; name@L764; existing@L766
# parameters: path@L43; path@L50; path@L55; project@L71; self@L71; path@L89; self@L89; name@L94; self@L94; value@L94; counts@L99; path@L99; self@L99; code@L110; column@L110; line@L110; message@L110; path@L110; self@L110; cases@L131; expected@L131; metric@L131; self@L131; tool@L131; evidence@L185; path@L185; evidence@L206; path@L206; evidence@L225; path@L225; evidence@L243; text@L243; node@L264; evidence@L280; command@L311; execute@L311; project@L311; work@L311; evidence@L329; execute@L329; root@L329; command@L539; evidence@L539; execute@L539; root@L539
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
        if len(self.findings) >= 1000:
            self.findings_truncated = True
            return
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


def cobertura(evidence: Evidence, path: Path) -> None:
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
                    "-fsyntax-only",
                    "-Wall",
                    "-Wextra",
                    "-Wunused",
                    "-fdiagnostics-format=json",
                    entry,
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
                ["php", "/opt/phpmd.phar", ",".join(evidence.sources), "json", "unusedcode"],
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
        tool, metric = "rustc/LLVM 14 lcov", "llvm-source-region-line"
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
            cobertura(evidence, output if output.exists() else output.with_suffix(".cobertura.xml"))
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
            ["llvm-profdata-14", "merge", "-sparse", *map(str, profiles), "-o", str(root / "rust.profdata")],
            timeout=15,
        )
        if result["exit_code"] != 0:
            raise ValueError(result["stderr"])
        output = root / "rust.lcov"
        result = execute(
            [
                "llvm-cov-14",
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
