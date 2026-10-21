# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: manifest(files, entry, language)@L32; test_multifile_unicode_syntax_and_no_source_execution(tmp_path)@L43; test_unused_and_unreachable_locations()@L62; test_physical_newlines_not_unicode_string_separators(separator)@L77; test_unused_false_positive_boundaries(text)@L100; test_cross_file_references_and_empty_or_unparseable_source()@L105; test_unrelated_module_names_do_not_hide_unused_imports_or_locals()@L118; test_structural_python_errors_and_other_language_offsets()@L134; test_toolchain_formats(entry, language, output)@L164; test_unmapped_failure_bounds_duplicates_ansi_and_generated_artifacts()@L176; test_tool_location_limit_and_fuzz_paths()@L195; test_api_and_exports_preserve_locations_and_escape(tmp_path)@L215; coverage_function(monkeypatch, tmp_path, data)@L254; test_coverage_exact_lists_multifile_unknown_and_generated_exclusion(monkeypatch, tmp_path)@L271; test_coverage_budget_and_missing_entry(monkeypatch, tmp_path)@L297; test_coverage_prioritizes_later_file_missing_lines(monkeypatch, tmp_path)@L309
# variables: name@L38; text@L38; sentinel@L45; project@L46; result@L53; dynamic@L54; item@L54; item@L56; syntax@L56; text@L64; result@L65; item@L66; located@L66; item@L73; text@L79; finding@L80; item@L82; project@L107; empty@L111; invalid@L113; result@L120; item@L128; located@L128; item@L131; result@L136; other@L138; result@L143; project@L166; result@L167; project@L178; evidence@L180; result@L189; project@L197; index@L198; output@L198; result@L199; item@L212; project@L217; token@L218; headers@L219; client@L220; review@L221; store@L223; revision@L224; run@L225; result@L226; exported@L242; html@L244; archive@L247; saved@L248; worker@L256; function@L257; node@L258; namespace@L261; project@L273; data@L274; measure@L285; result@L286; project@L299; data@L300; result@L303; project@L311; data@L312; result@L318
# parameters: entry@L32; files@L32; language@L32; tmp_path@L43; separator@L77; text@L100; entry@L164; language@L164; output@L164; tmp_path@L215; data@L254; monkeypatch@L254; tmp_path@L254; args@L265; kwargs@L265; monkeypatch@L271; tmp_path@L271; monkeypatch@L297; tmp_path@L297; monkeypatch@L309; tmp_path@L309
# </code-map>

"""Jason Stys: exact-location regressions, inert source only; no host target execution.

Worker coverage is tested as one extracted trusted function with mocked subprocesses.
Real compiler and coverage acceptance lives in scripts/worker_checks.py on Linux CI.
"""

import ast
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from studio.analysis import inspect_source
from studio.api import create_app
from studio.locations import tool_locations
from studio.models import Project
from studio.reports import bundle, html_report


def manifest(files, entry="main.py", language="python"):
    """Produce bounded authored fixtures that analyzers inspect without importing."""
    return Project(
        title="Location fixtures",
        language=language,
        entry=entry,
        files=[{"name": name, "content": text} for name, text in files],
        cases=[{"name": "oracle", "stdin": "", "stdout": "ok"}],
    )


def test_multifile_unicode_syntax_and_no_source_execution(tmp_path):
    """Each auxiliary file gets its own line origin; Unicode columns are characters, not bytes."""
    sentinel = tmp_path / "never-created"
    project = manifest(
        [
            ("main.py", f"open({str(sentinel)!r}, 'w')\nprint('ok')\n"),
            ("helper.py", "é = 1; eval('1')\n"),
            ("broken.py", "def bad(:\n    pass\n"),
        ]
    )
    result = inspect_source(project)
    dynamic = next(item for item in result["findings"] if item["code"] == "PY-DYNAMIC")
    assert (dynamic["file"], dynamic["line"], dynamic["column"]) == ("helper.py", 1, 8)
    syntax = next(item for item in result["findings"] if item["code"] == "PY-SYNTAX")
    assert syntax["file"] == "broken.py" and syntax["line"] == 1 and syntax["column"] > 0
    assert dynamic["source_sha256"] == hashlib.sha256(project.files[1].content.encode()).hexdigest()
    assert not sentinel.exists()


def test_unused_and_unreachable_locations():
    """Report unused import/function/local and direct unreachable statements, not comments or literals."""
    text = "import math\ndef unused():\n    leftover = 5\n    return 1\n    print('never')\n\n# eval('ignored')\ntext = 'shell=True'\n"
    result = inspect_source(manifest([("main.py", text)]))
    located = {(item["code"], item["line"]) for item in result["findings"]}
    assert located == {
        ("PY-UNUSED-IMPORT", 1),
        ("PY-UNUSED-FUNCTION", 2),
        ("PY-UNUSED-LOCAL", 3),
        ("PY-UNREACHABLE", 5),
    }
    assert all(item["file"] == "main.py" for item in result["findings"])


@pytest.mark.parametrize("separator", ["\n", "\r\n", "\r"])
def test_physical_newlines_not_unicode_string_separators(separator):
    """CRLF/CR normalize as Python does; literal Unicode line separators do not shift AST columns."""
    text = "example = 'a\u2028b'" + separator + "é = 1; eval('1')" + separator
    finding = next(
        item
        for item in inspect_source(manifest([("main.py", text)]))["findings"]
        if item["code"] == "PY-DYNAMIC"
    )
    assert (finding["line"], finding["column"]) == (2, 8)


@pytest.mark.parametrize(
    "text",
    [
        "import math\n__all__ = ['math']\n",
        "import math\n__all__ = get_exports()\n",
        "from __future__ import annotations\n",
        "def outer():\n    captured = 1\n    def inner():\n        return captured\n    return inner\nouter()\n",
        "def f(argument):\n    _intentional = 1\n    return argument\nf(1)\n",
        "class C:\n    field = 1\n    def method(self):\n        return self.field\n",
        "@register\ndef plugin():\n    return 1\n",
    ],
)
def test_unused_false_positive_boundaries(text):
    """Preserve exports/closures/parameters/intentional names/class APIs/decorated callbacks."""
    assert inspect_source(manifest([("main.py", text)]))["findings"] == []


def test_cross_file_references_and_empty_or_unparseable_source():
    """Conservatively recognize supplied callers and explicitly report missing parser locations."""
    project = manifest(
        [("main.py", "import helper\nprint(helper.work())\n"), ("helper.py", "def work():\n    return 1\n")]
    )
    assert inspect_source(project)["findings"] == []
    empty = inspect_source(manifest([("main.py", "")]))
    assert empty["files"]["main.py"]["parsed"]
    invalid = inspect_source(manifest([("main.py", "\x00")]))
    assert not invalid["files"]["main.py"]["parsed"]
    assert invalid["files"]["main.py"]["location_available"] is False


def test_unrelated_module_names_do_not_hide_unused_imports_or_locals():
    """A real browser regression: main's math usage cannot make helper's separate import used."""
    result = inspect_source(
        manifest(
            [
                ("main.py", "import math\nprint(math.pi)\ndef used(value):\n    print(value)\nused(1)\n"),
                ("helper.py", "import math\ndef unused():\n    value = 2\n    return 0\n"),
            ]
        )
    )
    located = {(item["file"], item["line"], item["code"]) for item in result["findings"]}
    assert ("helper.py", 1, "PY-UNUSED-IMPORT") in located
    assert ("helper.py", 3, "PY-UNUSED-LOCAL") in located
    assert not any(item["file"] == "main.py" for item in result["findings"])


def test_structural_python_errors_and_other_language_offsets():
    """Compiler symbol tables reject out-of-scope return; other text retains local offsets."""
    result = inspect_source(manifest([("main.py", "return 1\n")]))
    assert result["findings"][0]["code"] == "PY-SYNTAX"
    other = manifest(
        [("main.js", "console.log('ok');\n"), ("helper.js", "// header\neval('1');\n")],
        "main.js",
        "javascript",
    )
    result = inspect_source(other)
    assert (result["findings"][0]["file"], result["findings"][0]["line"]) == ("helper.js", 2)


@pytest.mark.parametrize(
    "entry,language,output",
    [
        ("main.py", "python", '  File "/tmp/project/main.py", line 2, in fail'),
        ("main.cpp", "cpp", "main.cpp:2:3: error: fixture"),
        ("main.c", "c", "./main.c:2:3: warning: fixture"),
        ("main.js", "javascript", "at fail (/tmp/project/main.js:2:3)"),
        ("main.ts", "typescript", "main.ts(2,3): error TS2304: fixture"),
        ("Main.java", "java", "at Main.fail(Main.java:2)"),
        ("main.cs", "csharp", "/tmp/project/main.cs(2,3): error CS1002: fixture"),  # noqa: S108 -- inert diagnostic fixture, never opened
        ("main.rs", "rust", " --> main.rs:2:3"),
        ("main.php", "php", "PHP Fatal error: fixture in /tmp/project/main.php on line 2"),
        ("main.sh", "bash", "main.sh: line 2: syntax error"),
        ("main.S", "assembly", "main.S:2: Error: fixture"),
        ("main.sql", "sql", '  File "sql_driver.py", line 2, in execute'),
    ],
)
def test_toolchain_formats(entry, language, output):
    """Map only actual source references; SQL generated-driver lines cannot identify SQL source."""
    project = manifest([(entry, "first\nsecond\nthird\n")], entry, language)
    result = tool_locations({"compilation": {"exit_code": 1, "stderr": output}}, project)
    if language == "sql":
        assert result["diagnostics"] == [] and result["unlocated_failures"]
    else:
        assert result["diagnostics"][0]["file"] == entry
        assert result["diagnostics"][0]["line"] == 2
        assert result["unlocated_failures"] == []


def test_unmapped_failure_bounds_duplicates_ansi_and_generated_artifacts():
    """Wrong answers have no fabricated location; generated pytest locations are labeled distinctly."""
    project = manifest([("main.py", "first\nsecond\n")])
    project.tests = "def test_fixture():\n    assert False\n"
    evidence = {
        "checks": {"cases": [{"passed": False, "name": "wrong answer", "stdout": "wrong"}]},
        "generated_tests": {"exit_code": 1, "stdout": "test_generated.py:2: AssertionError"},
        "compilation": {
            "exit_code": 1,
            "stderr": "\x1b[31mmain.py:2:3: error\x1b[0m\nmain.py:2:3: error\n../main.py:1: error\nmain.py:999: error\nmain.py:"
            + "9" * 5000,
        },
    }
    result = tool_locations(evidence, project)
    assert len(result["diagnostics"]) == 2
    assert result["diagnostics"][1]["artifact"] == "generated"
    assert result["unlocated_failures"][0]["stage"].startswith("case:")


def test_tool_location_limit_and_fuzz_paths():
    """Bound retained findings even if many tool lines differ; instrumented/fuzz logs are included."""
    project = manifest([("main.py", "print(1)\n")])
    output = "\n".join(f"main.py:1:{index + 1}: error" for index in range(1100))
    result = tool_locations(
        {
            "compilation": {"exit_code": 1, "stderr": output},
            "fuzz": {
                "status": "findings",
                "process": {"stderr": "main.py:1: crash"},
                "findings": [{"process": {"stderr": "main.py:1: crash"}}],
            },
        },
        project,
    )
    # Per-stream 8 KiB tail plus deduplication is smaller than the global cap.
    assert len(result["diagnostics"]) < 1000
    assert any(item["stage"] == "fuzz:0" for item in result["diagnostics"])


def test_api_and_exports_preserve_locations_and_escape(tmp_path):
    """Exercise real review API plus JSON/HTML/ZIP download with a located result, no Docker."""
    project = manifest([("main.py", "print('ok')\n"), ("helper.py", "import math\n")])
    token = "location-test-session-" + "x" * 32
    headers = {"Authorization": "Bearer " + token}
    with TestClient(create_app(tmp_path, token)) as client:
        review = client.post("/api/review", headers=headers, json=project.model_dump()).json()
        assert review["static"]["findings"][0]["file"] == "helper.py"
        store = client.app.state.store
        revision = store.create(project.model_dump())
        run = store.queue(revision["id"])
        result = {
            **review,
            "coverage": {
                "status": "measured",
                "files": {
                    "helper.py": {
                        "status": "measured",
                        "summary": {},
                        "missing_lines": [1],
                        "missing_branches": [[1, -1]],
                    }
                },
            },
        }
        result["static"]["findings"][0]["message"] = "<script>fixture</script>"
        store.finish(run, "completed", result)
        exported = client.get(f"/api/runs/{run}/report?format=json", headers=headers).json()
        assert exported["result"]["coverage"]["files"]["helper.py"]["missing_lines"] == [1]
        html = client.get(f"/api/runs/{run}/report?format=html", headers=headers).text
        assert "<script>" not in html and "&lt;script&gt;" in html
        assert "helper.py</td><td>1" in html and "Uncovered lines: 1" in html
        archive = client.get(f"/api/runs/{run}/report?format=zip", headers=headers).content
        with zipfile.ZipFile(io.BytesIO(archive)) as saved:
            assert json.loads(saved.read("report.json"))["result"] == result
    assert "Legacy" in html_report({"static": {"findings": [{"line": 1, "message": "old"}]}})
    assert bundle({"result": {}}, {"project": project.model_dump()})


def coverage_function(monkeypatch, tmp_path, data):
    """Load only the trusted coverage definition with inert tool stubs, never import the container worker."""
    worker = ast.parse(Path("runner/worker.py").read_text(encoding="utf-8"))
    function = next(
        node for node in worker.body if isinstance(node, ast.FunctionDef) and node.name == "coverage"
    )
    (tmp_path / "coverage.json").write_text(json.dumps(data), encoding="utf-8")
    namespace = {
        "WORK": tmp_path,
        "hashlib": hashlib,
        "json": json,
        "execute": lambda *args, **kwargs: {"exit_code": 0, "stderr": ""},
    }
    exec(compile(ast.Module(body=[function], type_ignores=[]), "trusted-coverage-test", "exec"), namespace)  # noqa: S102 -- trusted function only; mocked CLI, no submitted source execution
    return namespace["coverage"]


def test_coverage_exact_lists_multifile_unknown_and_generated_exclusion(monkeypatch, tmp_path):
    """Entry summary compatibility never discards known locations or assumes missing files are covered."""
    project = manifest([("main.py", "print(1)\n"), ("helper.py", "print(2)\n"), ("unknown.py", "print(3)\n")])
    data = {
        "files": {
            "main.py": {"summary": {"missing_lines": 0}, "executed_lines": [1]},
            "helper.py": {
                "summary": {"missing_lines": 1},
                "missing_lines": [1],
                "missing_branches": [[1, -1]],
            },
            "test_generated.py": {"summary": {}, "missing_lines": [999]},
        }
    }
    measure = coverage_function(monkeypatch, tmp_path, data)
    result = measure([], project.model_dump())
    assert result["status"] == "measured" and result["entry"] == {"missing_lines": 0}
    assert result["files"]["helper.py"]["missing_lines"] == [1]
    assert result["files"]["helper.py"]["missing_branches"] == [[1, -1]]
    assert result["files"]["unknown.py"]["status"] == "not-measured"
    assert "test_generated.py" not in result["files"]
    assert not result["locations_truncated"]
    assert measure([], {**project.model_dump(), "language": "cpp"})["status"] == "not-applicable"
    assert measure([], {**project.model_dump(), "cases": []})["status"] == "not-applicable"


def test_coverage_budget_and_missing_entry(monkeypatch, tmp_path):
    """Lists are explicitly truncated under a finite output budget; no entry data blocks measurement."""
    project = manifest([("main.py", "print(1)\n")]).model_dump()
    data = {
        "files": {"main.py": {"summary": {"missing_lines": 21000}, "missing_lines": list(range(1, 21001))}}
    }
    result = coverage_function(monkeypatch, tmp_path, data)([], project)
    assert len(result["files"]["main.py"]["missing_lines"]) == 20000
    assert result["locations_truncated"] and result["files"]["main.py"]["truncated"]
    assert coverage_function(monkeypatch, tmp_path, {"files": {}})([], project)["status"] == "blocked"


def test_coverage_prioritizes_later_file_missing_lines(monkeypatch, tmp_path):
    """A large fully covered entry cannot consume the location budget before helper gaps are retained."""
    project = manifest([("main.py", "print(1)\n"), ("helper.py", "print(2)\n")]).model_dump()
    data = {
        "files": {
            "main.py": {"summary": {"missing_lines": 0}, "executed_lines": list(range(1, 21001))},
            "helper.py": {"summary": {"missing_lines": 1}, "missing_lines": [1]},
        }
    }
    result = coverage_function(monkeypatch, tmp_path, data)([], project)
    assert result["files"]["helper.py"]["missing_lines"] == [1]
    assert result["files"]["main.py"]["truncated"]
