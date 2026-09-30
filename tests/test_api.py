# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: client(tmp_path)@L22; test_auth_and_origin(client, project)@L28; test_revision_reports(client, project)@L40; test_no_provider(client, project)@L58; test_export_iteration_history(client, project)@L67; test_blocked_execution_retained(client, project, monkeypatch)@L88; blocked(_project)@L91; test_compare_unrelated(client, project)@L103
# variables: TOKEN@L17; AUTH@L18; value@L24; response@L36; saved@L42; store@L49; identifier@L50; format@L52; result@L53; body@L60; result@L63; store@L69; original@L70; candidate@L71; unrelated@L72; revision@L73; identifier@L74; run@L78; exported@L79; timeline@L80; row@L81; saved@L95; job@L96; result@L98; store@L105; runs@L106; _@L107; saved@L108
# parameters: tmp_path@L22; client@L28; project@L28; client@L40; project@L40; client@L58; project@L58; client@L67; project@L67; client@L88; monkeypatch@L88; project@L88; _project@L91; client@L103; project@L103
# </code-map>

"""API security, asynchronous execution and failure semantics. Symbols: docs/code-index.md."""

import pytest
from fastapi.testclient import TestClient

from studio import execution
from studio.api import create_app

TOKEN = "test-session-token-" + "x" * 32
AUTH = {"Authorization": "Bearer " + TOKEN}


@pytest.fixture
def client(tmp_path):
    """Start a private temporary app with no production provider credentials."""
    with TestClient(create_app(tmp_path, TOKEN)) as value:
        yield value


def test_auth_and_origin(client, project):
    """Untrusted webpages and unauthenticated clients cannot submit executable jobs."""
    assert client.get("/health").status_code == 200
    assert client.get("/api/revisions").status_code == 401
    assert client.get("/api/revisions", headers=AUTH).status_code == 200
    assert client.get("/api/revisions", headers={**AUTH, "Origin": "https://evil.example"}).status_code == 403
    assert client.get("/health", headers={"Host": "evil.example"}).status_code == 403
    assert client.post("/api/revisions", headers=AUTH, content="x" * 1600000).status_code == 413
    response = client.post("/api/revisions", headers=AUTH, json=project.model_dump())
    assert response.status_code == 200 and response.headers["x-content-type-options"] == "nosniff"


def test_revision_reports(client, project):
    """Saved revisions, errors and inert report formats are predictable."""
    saved = client.post("/api/revisions", headers=AUTH, json=project.model_dump()).json()
    assert client.get(f"/api/revisions/{saved['id']}", headers=AUTH).json()["project"] == project.model_dump()
    assert client.get("/api/revisions/missing", headers=AUTH).status_code == 404
    assert client.post("/api/revisions/missing/run", headers=AUTH).status_code == 404
    assert client.get("/api/runs/missing", headers=AUTH).status_code == 404
    assert client.get("/api/runs/missing/report", headers=AUTH).status_code == 404
    assert len(client.get("/api/catalog", headers=AUTH).json()) == 48
    store = client.app.state.store
    identifier = store.queue(saved["id"])
    store.finish(identifier, "completed", {"log": "<script>"})
    for format in ("json", "html", "zip"):
        result = client.get(f"/api/runs/{identifier}/report?format={format}", headers=AUTH)
        assert result.status_code == 200
    assert client.get(f"/api/runs/{identifier}/report?format=exe", headers=AUTH).status_code == 400


def test_no_provider(client, project):
    """No real provider is never represented as successful AI generation."""
    body = {"task": "improve", "project": project.model_dump(), "consent": False}
    assert client.post("/api/ai", headers=AUTH, json=body).status_code == 400
    body["consent"] = True
    result = client.post("/api/ai", headers=AUTH, json=body)
    assert result.status_code == 400 and "No AI provider" in result.text


def test_export_iteration_history(client, project):
    """Reports retain linked revision metrics and do not leak another project's source/history."""
    store = client.app.state.store
    original = store.create(project.model_dump())
    candidate = store.create(project.model_dump(), original["id"])
    unrelated = store.create(project.model_dump())
    for revision in (original, candidate, unrelated):
        identifier = store.queue(revision["id"])
        store.finish(
            identifier, "completed", {"checks": {"passed": 1, "failed": 0}, "benchmark": {"median_ms": 3}}
        )
    run = store.runs(candidate["id"])[0]
    exported = client.get(f"/api/runs/{run['id']}/report?format=json", headers=AUTH).json()
    timeline = exported["iteration_history"]
    assert [row["id"] for row in timeline["revisions"]] == [original["id"], candidate["id"]]
    assert timeline["revisions"][1]["attempts"][0]["benchmark"]["median_ms"] == 3
    assert timeline["revisions"][1]["parent_id"] == original["id"]
    assert len(timeline["revisions"][0]["snapshot_sha256"]) == 64
    assert "files" not in timeline["revisions"][0]


def test_blocked_execution_retained(client, project, monkeypatch):
    """A missing worker still produces durable blocked evidence, not a false pass."""

    async def blocked(_project):
        return {"tool_status": "blocked", "reason": "No isolated worker"}

    monkeypatch.setattr(execution, "run", blocked)
    saved = client.post("/api/revisions", headers=AUTH, json=project.model_dump()).json()
    job = client.post(f"/api/revisions/{saved['id']}/run", headers=AUTH).json()
    # A subsequent request crosses the background task scheduling boundary.
    result = client.get(f"/api/runs/{job['id']}", headers=AUTH).json()
    assert result["status"] in {"running", "blocked"}
    assert client.get("/api/revisions", headers=AUTH).json()[0]["id"] == saved["id"]


def test_compare_unrelated(client, project):
    """Different projects and nonexistent attempts cannot be ranked."""
    store = client.app.state.store
    runs = []
    for _ in range(2):
        saved = store.create(project.model_dump())
        runs.append(store.queue(saved["id"]))
    assert client.get(f"/api/compare?baseline={runs[0]}&candidate={runs[1]}", headers=AUTH).status_code == 400
    assert client.get("/api/compare?baseline=missing&candidate=missing", headers=AUTH).status_code == 404
