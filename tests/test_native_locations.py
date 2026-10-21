# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: evidence(language, source)@L39; test_source_binding_union_and_partial()@L46; test_unknown_and_location_budget()@L67; test_gcov_lcov_and_branch_ids(tmp_path)@L80; test_xml_coverage_and_reject_entities(tmp_path)@L106; test_shell_ast_and_assembly_exports()@L129; test_sql_statement_start_anchors(text, lines)@L154; test_bounded_tools_fail_closed(tmp_path, language)@L160; unavailable()@L166; test_controller_rebinds_native_findings_and_escapes()@L175
# variables: project@L41; item@L48; result@L53; item@L69; line@L71; result@L72; index@L75; item@L82; path@L83; item@L108; path@L109; item@L137; finding@L139; item@L156; _@L162; project@L162; work@L163; coverage@L170; unused@L170; _@L177; project@L177; item@L178; raw@L180; result@L181; report@L184
# parameters: language@L39; source@L39; tmp_path@L80; tmp_path@L106; lines@L154; text@L154; language@L160; tmp_path@L160; args@L166; kwargs@L166
# </code-map>

"""Jason Stys: inert native-report parser regressions; never execute submitted programs on the host.

Real measurements are separate acceptance fixtures in scripts/worker_checks.py on restricted Linux CI.
Symbol/parameter/variable declaration map: docs/code-index.md.
"""

import gzip
import hashlib
import json

import pytest

from examples.language_locations import SAMPLES, location_fixture
from runner.language_checks import (
    Evidence,
    assembly_symbols,
    cobertura,
    gcov,
    jacoco,
    lcov,
    native_checks,
    read_json,
    read_xml,
    shell_lines,
)
from runner.sql_runtime import statements
from studio.locations import tool_locations
from studio.reports import html_report


def evidence(language="cpp", source="first\nsecond\nthird\n"):
    """Construct a pure parser record, never import worker.py or a target module."""
    project = location_fixture(language)[0].model_dump()
    project["files"][0]["content"] = source
    return Evidence(project)


def test_source_binding_union_and_partial():
    """Unknown paths, out-of-range references and incomplete cases cannot claim full coverage."""
    item = evidence()
    assert item.name("/elsewhere/main.cpp") is None
    assert item.name("../../main.cpp") is None
    item.add_lines("/tmp/project/main.cpp", {1: 0, 2: 1, 999: 1})  # noqa: S108 -- inert tool path
    item.add_lines("./main.cpp", {1: 1, 2: 0, 3: 0})
    result = item.coverage("test tool", "test metric", [{"exit_code": 1}], 1)
    assert result["status"] == "partial"
    assert result["files"]["main.cpp"]["missing_lines"] == [3]
    assert result["files"]["main.cpp"]["executed_lines"] == [1, 2]
    assert (
        item.coverage("tool", "metric", [{"exit_code": 1, "expected_exit_code": 1}], 1)["status"]
        == "measured"
    )
    item.finding("main.cpp", 2, 3, "UNUSED", "Review")
    item.finding("/elsewhere/main.cpp", 2, 3, "BAD", "Ignore")
    assert len(item.findings) == 1
    assert item.findings[0]["source_sha256"] == hashlib.sha256(b"first\nsecond\nthird\n").hexdigest()


def test_unknown_and_location_budget():
    """A missing native report is unknown, and shared location lists are explicitly bounded."""
    item = evidence(source="line\n" * 22000)
    assert item.coverage("tool", "metric", [], 0)["status"] == "blocked"
    item.add_lines("main.cpp", {line: 0 for line in range(1, 22001)})
    result = item.coverage("tool", "metric", [], 0)
    assert len(result["files"]["main.cpp"]["missing_lines"]) == 20000
    assert result["locations_truncated"]
    for index in range(1001):
        item.finding("main.cpp", 1, 1, "unused", f"candidate {index}")
    assert len(item.findings) == 1000 and item.findings_truncated


def test_gcov_lcov_and_branch_ids(tmp_path):
    """Preserve actual native branch IDs/counts without fabricating destination line arcs."""
    item = evidence()
    path = tmp_path / "gcov.gz"
    path.write_bytes(
        gzip.compress(
            json.dumps(
                {
                    "files": [
                        {
                            "file": "main.cpp",
                            "lines": [{"line_number": 2, "count": 0, "branches": [{"count": 0}]}],
                        }
                    ]
                }
            ).encode()
        )
    )
    gcov(item, path)
    assert item.counts["main.cpp"][2] == 0
    assert item.branches["main.cpp"][0]["branch_id"] == 0
    lcov(item, "SF:main.cpp\nDA:2,1\nDA:3,0\nBRDA:2,0,1,-\nend_of_record\n")
    assert item.counts["main.cpp"] == {2: 1, 3: 0}
    assert item.branches["main.cpp"][-1]["hits"] == 0


def test_xml_coverage_and_reject_entities(tmp_path):
    """Only the known JaCoCo declaration is removed; arbitrary entity/DTD input is rejected."""
    item = evidence("java")
    path = tmp_path / "report.xml"
    path.write_text(
        '<!DOCTYPE report PUBLIC "-//JACOCO//DTD Report 1.1//EN" "report.dtd"><report><package><sourcefile name="Main.java"><line nr="2" mi="1" ci="0" mb="1" cb="1"/></sourcefile></package></report>'
    )
    jacoco(item, path)
    assert item.counts["Main.java"][2] == 0
    assert item.branches["Main.java"][0]["missing"] == 1
    path.write_text(
        '<coverage><class filename="Main.java"><lines><line number="3" hits="2"/></lines></class></coverage>'
    )
    cobertura(item, path)
    assert item.counts["Main.java"][3] == 2
    path.write_text('<!DOCTYPE report [<!ENTITY x SYSTEM "file:///secret">]><report>&x;</report>')
    with pytest.raises(ValueError, match="DTD"):
        read_xml(path)
    path.write_bytes(b" " * (8 * 1024 * 1024 + 1))
    with pytest.raises(ValueError, match="eight MiB"):
        read_json(path)


def test_shell_ast_and_assembly_exports():
    """Shell universe is AST-based; exported and referenced assembly labels are not unused candidates."""
    assert shell_lines(
        {
            "Type": "File",
            "Stmts": [{"Type": "CallExpr", "Pos": {"Line": 3}}, {"Type": "Comment", "Pos": {"Line": 4}}],
        }
    ) == {3}
    item = evidence("assembly", ".global entry\nentry:\n jmp used\nunused:\n ret\nused:\n ret\n")
    assembly_symbols(item)
    assert [(finding["file"], finding["line"]) for finding in item.findings] == [("main.S", 4)]


@pytest.mark.parametrize(
    "text,lines",
    [
        ("-- comment\nSELECT ';';\n/* start */ SELECT 2;", [2, 3]),
        (
            "CREATE TABLE t(x);\nCREATE TRIGGER tr AFTER INSERT ON t BEGIN SELECT 1; SELECT 2; END;\nSELECT 3;",
            [1, 2, 3],
        ),
        ("SELECT 1; -- trailing only", [1]),
        ("/* only comment */", []),
    ],
)
def test_sql_statement_start_anchors(text, lines):
    """SQLite's parser keeps quoted semicolons and trigger bodies in one original statement."""
    assert [item["line"] for item in statements(text)] == lines


@pytest.mark.parametrize("language", SAMPLES)
def test_bounded_tools_fail_closed(tmp_path, language):
    """Unavailable tools remain blocked rather than fake successful unused/coverage checks."""
    project, _, _ = location_fixture(language)
    work = tmp_path / language
    work.mkdir()

    def unavailable(*args, **kwargs):
        """Return an inert missing-tool result without launching any command."""
        return {"exit_code": None, "stderr": "missing tool", "stdout": "", "timeout": False}

    coverage, unused = native_checks(project.model_dump(), work, unavailable, ["not-executed"])
    assert coverage["status"] == "blocked"
    assert unused["status"] == ("completed" if language == "assembly" else "blocked")


def test_controller_rebinds_native_findings_and_escapes():
    """Stale/malicious native locations cannot become trusted UI findings or executable report markup."""
    project, _, _ = location_fixture("javascript")
    item = Evidence(project.model_dump())
    item.finding(project.entry, 1, 1, "unused", "<script>bad</script>")
    raw = {"unused": {"findings": item.findings + [{**item.findings[0], "source_sha256": "wrong"}]}}
    result = tool_locations(raw, project)
    assert len(result["diagnostics"]) == 1
    assert result["diagnostics"][0]["stage"] == "unused-code"
    report = html_report({**raw, **result})
    assert "&lt;script&gt;bad&lt;/script&gt;" in report
    assert "<script>bad</script>" not in report
