# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_unsafe_names(name)@L45; test_safe_flat_names(suffix)@L52; test_project_invalid(project, changes)@L71; test_invalid_binary(project)@L77; test_zero_weights()@L85; test_history_retains_oracles(tmp_path, project)@L91; test_history_restart(tmp_path, project)@L110; test_reports_escaped(project)@L121; test_static_no_execution(project, tmp_path)@L131; test_comparison_gates()@L140; test_catalog_no_fake_passes()@L165; test_training_split()@L174; test_training_bad_data(tmp_path, rows)@L192
# variables: payload@L79; store@L93; payload@L94; initial@L96; candidate@L97; change@L102; store@L112; revision@L113; run@L114; restarted@L115; run@L123; report@L124; archive@L126; sentinel@L133; payload@L134; result@L136; valid@L142; candidate@L150; changes@L152; rows@L167; row@L168; row@L171; result@L176; train@L176; validation@L176; row@L177; path@L194; row@L195
# parameters: name@L45; suffix@L52; changes@L71; project@L71; project@L77; project@L91; tmp_path@L91; project@L110; tmp_path@L110; project@L121; project@L131; tmp_path@L131; rows@L192; tmp_path@L192
# </code-map>

"""Input boundary, history and comparison invariants. Symbols: docs/code-index.md."""

import io
import json
import zipfile
from pathlib import Path

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from studio.analysis import compare, inspect_source
from studio.catalog import catalog
from studio.models import Priorities, Project, SourceFile
from studio.reports import bundle, html_report
from studio.store import Store
from training.dataset import prepare


@pytest.mark.parametrize(
    "name",
    [
        "../a.py",
        "-flag",
        ".env",
        "a/b.py",
        "a\\b.py",
        "a..py",
        "CON.py",
        "com1",
        "LPT9.txt",
        "a\x00.py",
        "a b.py",
    ],
)
def test_unsafe_names(name):
    """All platform and traversal aliases fail before filesystem access."""
    with pytest.raises(ValidationError):
        SourceFile(name=name, content="")


@given(st.text(alphabet="abcdefXYZ012_-", min_size=0, max_size=30))
def test_safe_flat_names(suffix):
    """Safe generated names never acquire directory components."""
    assert SourceFile(name="main" + suffix + ".py", content="").name.startswith("main")


@pytest.mark.parametrize(
    "changes",
    [
        {"files": [{"name": "main.py", "content": "a"}, {"name": "MAIN.py", "content": "b"}]},
        {"entry": "missing.py"},
        {"fuzz_methods": ["unknown"]},
        {"fuzz_methods": ["mutation", "mutation"]},
        {"fuzz_cases": 129},
        {"benchmark_repeats": 0},
        {"language": "unknown"},
        {"extra": True},
        {"files": [{"name": "main.py", "encoding": "base64", "content": "aGVsbG8="}]},
    ],
)
def test_project_invalid(project, changes):
    """Reject incoherent and excessive execution manifests."""
    with pytest.raises(ValidationError):
        Project.model_validate({**project.model_dump(), **changes})


def test_invalid_binary(project):
    """Invalid attachment bytes cannot reach a worker."""
    payload = project.model_dump()
    payload["files"].append({"name": "data.bin", "content": "???", "encoding": "base64"})
    with pytest.raises(ValidationError):
        Project.model_validate(payload)


def test_zero_weights():
    """A ranking cannot have a zero denominator."""
    with pytest.raises(ValidationError):
        Priorities(runtime=0, memory=0, readability=0, footprint=0)


def test_history_retains_oracles(tmp_path, project):
    """Candidates cannot rewrite the baseline expectations or harness."""
    store = Store(tmp_path / "state.db")
    payload = project.model_dump()
    payload["tests"] = "def test_contract(): assert True\n"
    initial = store.create(payload)
    candidate = store.create(
        {**payload, "tests": payload["tests"] + "def test_more(): assert True\n"}, initial["id"]
    )
    assert candidate["parent_id"] == initial["id"]
    assert store.revision(initial["id"])["project"]["tests"] == payload["tests"]
    for change in ({"cases": []}, {"tests": ""}, {"language": "javascript"}):
        with pytest.raises(ValueError):
            store.create({**payload, **change}, initial["id"])
    with pytest.raises(KeyError):
        store.create(payload, "missing")
    assert len(store.history()) == 2


def test_history_restart(tmp_path, project):
    """Process loss leaves interrupted evidence, not an evergreen running state."""
    store = Store(tmp_path / "state.db")
    revision = store.create(project.model_dump())
    run = store.queue(revision["id"])
    restarted = Store(tmp_path / "state.db")
    assert restarted.run(run)["status"] == "interrupted"
    with pytest.raises(KeyError):
        restarted.run("missing")


def test_reports_escaped(project):
    """Hostile logs remain text in HTML and paths remain safe in ZIP exports."""
    run = {"status": "completed", "result": {"log": '<script>alert("x")</script>'}}
    report = html_report(run)
    assert "<script>" not in report and "&lt;script&gt;" in report
    with zipfile.ZipFile(io.BytesIO(bundle(run, {"project": project.model_dump()}))) as archive:
        assert "source/main.py" in archive.namelist()
        assert json.loads(archive.read("report.json"))["status"] == "completed"


def test_static_no_execution(project, tmp_path):
    """AST inspection does not import a source module with side effects."""
    sentinel = tmp_path / "not-created"
    payload = project.model_dump()
    payload["files"][0]["content"] = f"open({str(sentinel)!r}, 'w').write('x')\neval('1')\n"
    result = inspect_source(Project.model_validate(payload))
    assert result["findings"] and not sentinel.exists()


def test_comparison_gates():
    """Correctness, independent tests, environments and warnings gate soft weighted scores."""
    valid = {
        "tool_status": "completed",
        "checks": {"passed": 2, "failed": 0},
        "oracle_hash": "same",
        "environment": {"cpu": "same"},
        "benchmark": {"median_ms": 10, "max_rss_kib": 100},
        "static": {"source_bytes": 100, "long_lines": 2, "findings": []},
    }
    candidate = {**valid, "benchmark": {"median_ms": 5, "max_rss_kib": 100}}
    assert compare(valid, candidate, Priorities().model_dump())["score"] > 0
    for changes in (
        {"tool_status": "blocked"},
        {"checks": {"passed": 0}},
        {"checks": {"passed": 2, "failed": 1}},
        {"oracle_hash": "different"},
        {"environment": {}},
        {"generated_tests": {"exit_code": 1}},
        {"fuzz": {"status": "findings"}},
        {"static": {"findings": ["warning"]}},
    ):
        assert not compare(valid, {**candidate, **changes}, Priorities().model_dump())["eligible"]


def test_catalog_no_fake_passes():
    """All 48 reference categories retain applicability rather than a fabricated result."""
    rows = catalog()
    assert len(rows) == 48 and len({row["id"] for row in rows}) == 48
    assert rows[43]["mode"] == "external"
    assert rows[19]["mode"] == "manual"
    assert all("passed" not in row for row in rows)


def test_training_split():
    """Project groups and normalized prompts never leak across evaluation splits."""
    train, validation, result = prepare(Path("examples/training.jsonl"))
    assert {row["project"] for row in train}.isdisjoint(row["project"] for row in validation)
    assert result["project_disjoint"] and result["validation_records"] > 0


@pytest.mark.parametrize(
    "rows",
    [
        [{"prompt": "x", "completion": "y", "project": "p", "license": "unlicensed"}],
        [{"prompt": "x", "completion": "y", "project": "p", "license": "owned"}],
        [
            {"prompt": "x", "completion": "y", "project": "a", "license": "owned"},
            {"prompt": "x", "completion": "z", "project": "b", "license": "owned"},
        ],
    ],
)
def test_training_bad_data(tmp_path, rows):
    """Missing rights, insufficient groups and conflicting labels are rejected."""
    path = tmp_path / "data.jsonl"
    path.write_text("\n".join(json.dumps(row) for row in rows))
    with pytest.raises(ValueError):
        prepare(path)
