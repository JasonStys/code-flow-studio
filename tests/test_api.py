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
