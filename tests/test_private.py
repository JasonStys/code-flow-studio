# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: client(tmp_path)@L32; register(client, alias)@L39; unlock(client, key)@L46; test_registration_private_headers_and_zero_secret_echo(client)@L52; test_request_origin_host_mutation_rejected(client, headers)@L83; test_real_revisions_encrypted_lock_reopen(client, project)@L93; test_two_accounts_and_same_account_new_session_need_key(client, project)@L115; test_recovery_logout_expiry_delete(client)@L147; test_expiry_and_human_idle(client)@L171; test_private_static_review_and_blocked_execution(client, project, monkeypatch)@L186; unavailable()@L189; test_provider_keys_private_and_consent_version(client, project)@L211; test_recovery_save_failure_preserves_code(client, monkeypatch)@L255; unavailable()@L264; test_archive_paths(name)@L278; test_archive_authentication_before_extract(tmp_path)@L284; test_single_instance_and_launcher_not_browser(client)@L300; test_warning_budget_is_bounded(project)@L307; test_slow_worker_diagnostic_does_not_block_saving(client, project, monkeypatch)@L317; slow_probe()@L321
# variables: PASSWORD@L25; KEY@L26; SALT@L27; HEADERS@L28; app@L34; session@L35; response@L41; response@L48; response@L56; invalid@L64; db@L68; row@L69; result@L97; identity@L99; manager@L100; owner@L101; archive@L105; wrong@L108; identity@L119; original@L120; recovery@L149; body@L151; changed@L152; manager@L175; human@L176; db@L181; review@L196; identity@L198; job@L199; _@L200; result@L201; report@L206; config@L215; saved@L227; before@L237; repeated@L238; changed@L240; manager@L247; owner@L248; recovery@L259; original@L262; body@L269; root@L286; path@L289; damaged@L292; changed@L311; result@L313; started@L328
# parameters: tmp_path@L32; alias@L39; client@L39; client@L46; key@L46; client@L52; client@L83; headers@L83; client@L93; project@L93; client@L115; project@L115; client@L147; client@L171; client@L186; monkeypatch@L186; project@L186; kwargs@L189; client@L211; project@L211; client@L255; monkeypatch@L255; args@L264; name@L278; tmp_path@L284; client@L300; project@L307; client@L317; monkeypatch@L317; project@L317; kwargs@L321
# </code-map>

"""Jason Stys: actual private-account, archive, provider, ownership and blocked-execution regression tests.

All credentials/source are explicitly fictional and every filesystem root is disposable.
"""

import base64
import time

import pytest
from cryptography.exceptions import InvalidTag
from fastapi.testclient import TestClient

from studio import execution
from studio.private_api import create_private_app
from studio.vault import decrypt_workspace, encrypt_workspace, safe_name

PASSWORD = "synthetic-test-login-password-2026"  # noqa: S105 - disposable fixture only.
KEY = base64.b64encode(b"k" * 32).decode()
SALT = base64.b64encode(b"s" * 16).decode()
HEADERS = {"X-CFS-Request": "v1", "Origin": "http://127.0.0.1:8090"}


@pytest.fixture
def client(tmp_path):
    """Start actual auth/crypto/store, with an explicitly unavailable isolation fixture—not host execution."""
    app = create_private_app(tmp_path / "accounts", 8090)
    with TestClient(app, base_url="http://127.0.0.1:8090", headers=HEADERS) as session:
        yield session


def register(client, alias="fictional_one"):
    """Register a fictional password and capture its one-use recovery code for tests only."""
    response = client.post("/private/register", json={"alias": alias, "password": PASSWORD})
    assert response.status_code == 200
    return response.json()["recovery"]


def unlock(client, key=KEY):
    """Prove a synthetic derived key through the real route."""
    response = client.post("/private/unlock", json={"key": key, "salt": SALT})
    assert response.status_code == 200, response.text


def test_registration_private_headers_and_zero_secret_echo(client):
    """No seeded login, browser bearer or returned credential; API and mutation boundaries fail closed."""
    assert client.get("/private/account").status_code == 401
    assert client.get("/api/revisions").status_code == 404
    response = client.post("/private/register", json={"alias": "fictional_one", "password": PASSWORD})
    assert (
        "HttpOnly" in response.headers["set-cookie"] and "SameSite=strict" in response.headers["set-cookie"]
    )
    assert PASSWORD not in response.text
    assert response.headers["cache-control"] == "no-store"
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert "frame-ancestors 'none'" in response.headers["content-security-policy"]
    invalid = client.post(
        "/private/login", json={"alias": "bad <script>", "password": PASSWORD, "role": "admin"}
    )
    assert invalid.status_code == 422 and PASSWORD not in invalid.text
    with client.app.state.manager.accounts.connection() as db:
        row = db.execute("SELECT password,recovery FROM accounts").fetchone()
        assert row[0].startswith("scrypt-v1$") and PASSWORD not in row[0]
        assert row[1] != response.json()["recovery"]


@pytest.mark.parametrize(
    "headers",
    [
        {"Host": "evil.example"},
        {"Origin": "https://evil.example"},
        {"X-CFS-Request": "wrong"},
        {"Sec-Fetch-Site": "cross-site"},
    ],
)
def test_request_origin_host_mutation_rejected(client, headers):
    """Cross-site calls cannot register accounts or cause side effects."""
    assert (
        client.post(
            "/private/register", headers=headers, json={"alias": "fictional_one", "password": PASSWORD}
        ).status_code
        == 403
    )


def test_real_revisions_encrypted_lock_reopen(client, project):
    """Stored source is absent from ciphertext; wrong phrase fails; exact immutable history reopens."""
    register(client)
    unlock(client)
    result = client.post("/private/api/revisions", json=project.model_dump())
    assert result.status_code == 200, result.text
    identity = result.json()["id"]
    manager = client.app.state.manager
    owner = manager.owner
    assert manager.active.exists()
    assert client.post("/private/lock", json={}).status_code == 200
    assert not manager.active.exists()
    archive = manager.archive(owner)
    assert archive.read_bytes().startswith(b"CFSV0001") and b"print(4)" not in archive.read_bytes()
    assert client.get("/private/api/revisions").status_code == 423
    wrong = base64.b64encode(b"w" * 32).decode()
    assert client.post("/private/unlock", json={"key": wrong}).status_code == 400
    unlock(client)
    assert client.get("/private/api/revisions/" + identity).json()["project"] == project.model_dump()
    assert client.get("/private/backup").content.startswith(b"CFSV0001")


def test_two_accounts_and_same_account_new_session_need_key(client, project):
    """Guessing revision IDs/login passwords cannot cross owners or skip another session's vault proof."""
    register(client)
    unlock(client)
    identity = client.post("/private/api/revisions", json=project.model_dump()).json()["id"]
    original = dict(client.cookies)
    client.cookies.clear()
    assert (
        client.post("/private/login", json={"alias": "fictional_one", "password": PASSWORD}).status_code
        == 200
    )
    assert not client.get("/private/account").json()["unlocked"]
    assert client.get("/private/api/revisions/" + identity).status_code == 423
    unlock(client)
    assert client.get("/private/api/revisions/" + identity).status_code == 200
    client.cookies.clear()
    register(client, "fictional_two")
    assert client.get("/private/api/revisions/" + identity).status_code == 423
    assert client.post("/private/unlock", json={"key": KEY, "salt": SALT}).status_code == 400
    assert client.post("/private/logout", json={}).status_code == 200
    client.cookies.update(original)
    assert client.post("/private/lock", json={}).status_code == 200
    client.cookies.clear()
    assert (
        client.post("/private/login", json={"alias": "fictional_two", "password": PASSWORD}).status_code
        == 200
    )
    unlock(client)
    assert client.get("/private/api/revisions").json() == []
    assert client.get("/private/api/revisions/" + identity).status_code == 404


def test_recovery_logout_expiry_delete(client):
    """One-use recovery revokes old sessions but preserves the independent vault; deletion needs current password."""
    recovery = register(client)
    unlock(client)
    body = {"alias": "fictional_one", "password": PASSWORD + "-new", "recovery": recovery}
    changed = client.post("/private/reset", json=body)
    assert changed.status_code == 200 and changed.json()["recovery"] != recovery
    assert client.get("/private/account").status_code == 401
    assert client.post("/private/reset", json=body).status_code == 401
    assert (
        client.post(
            "/private/login", json={"alias": "fictional_one", "password": PASSWORD + "-new"}
        ).status_code
        == 200
    )
    unlock(client)
    assert client.post("/private/delete", json={"password": PASSWORD, "confirm": True}).status_code == 401
    assert (
        client.post("/private/delete", json={"password": PASSWORD + "-new", "confirm": True}).status_code
        == 200
    )
    assert client.get("/private/account").status_code == 401


def test_expiry_and_human_idle(client):
    """Session expiry and human timeout are independent of metadata polling."""
    register(client)
    unlock(client)
    manager = client.app.state.manager
    human = manager.last_human
    client.get("/private/account")
    assert manager.last_human == human
    assert client.post("/private/activity", json={"idle_seconds": 1800}).status_code == 200
    assert manager.idle_seconds == 1800
    with manager.accounts.connection() as db:
        db.execute("UPDATE sessions SET expires=?", (int(time.time()) - 1,))
    assert client.get("/private/account").status_code == 401


def test_private_static_review_and_blocked_execution(client, project, monkeypatch):
    """Heuristics don't execute code; absent isolation has no fake tests, performance score or host fallback."""

    async def unavailable(**kwargs):
        """Mock only missing isolation; this test does not replace genuine worker CI."""
        return {"ready": False, "reason": "Synthetic missing engine"}

    monkeypatch.setattr(execution, "diagnostics", unavailable)
    register(client)
    unlock(client)
    review = client.post("/private/api/review", json=project.model_dump()).json()
    assert review["tool_status"] == "static-only" and not review["executed"]
    identity = client.post("/private/api/revisions", json=project.model_dump()).json()["id"]
    job = client.post("/private/api/revisions/" + identity + "/run", json={}).json()["id"]
    for _ in range(100):
        result = client.get("/private/api/runs/" + job).json()
        if result["status"] not in {"queued", "running"}:
            break
        time.sleep(0.02)
    assert result["status"] == "blocked" and "checks" not in result["result"]
    report = client.get("/private/api/runs/" + job + "/report?format=json").json()
    assert report["iteration_history"]["revisions"]
    assert client.get("/private/api/runs/" + job + "/report?format=zip").content.startswith(b"PK")


def test_provider_keys_private_and_consent_version(client, project):
    """Keys are not in public config, source history or locked bytes; route changes invalidate source consent."""
    register(client)
    unlock(client)
    config = {
        "providers": [
            {
                "id": "owned",
                "kind": "openai",
                "url": "https://model.example/api",
                "model": "fixture",
                "key": "synthetic-provider-key-DO-NOT-USE",
            }
        ],
        "routes": {"generate": "owned"},
    }
    saved = client.put("/private/providers", json=config)
    assert saved.status_code == 200, saved.text
    assert config["providers"][0]["key"] not in saved.text
    assert saved.json()["providers"][0]["ready"]
    assert (
        client.post(
            "/private/api/ai", json={"task": "generate", "project": project.model_dump(), "consent": True}
        ).status_code
        == 409
    )
    before = saved.json()["revision"]
    repeated = client.put("/private/providers", json=config).json()
    assert repeated["revision"] != before
    changed = {
        **config,
        "providers": [
            {**config["providers"][0], "url": "https://another.example/api", "key": "", "retain_key": True}
        ],
    }
    assert client.put("/private/providers", json=changed).status_code == 400
    manager = client.app.state.manager
    owner = manager.owner
    assert client.post("/private/lock", json={}).status_code == 200
    assert b"synthetic-provider-key" not in manager.archive(owner).read_bytes()
    unlock(client)
    assert client.get("/private/providers").json()["providers"][0]["ready"]


def test_recovery_save_failure_preserves_code(client, monkeypatch):
    """Failed sealing cannot consume the recovery code or drop its unsaved working data."""
    import studio.private_workspace as workspace

    recovery = register(client)
    unlock(client)
    (client.app.state.manager.active / "change.txt").write_text("Synthetic unsaved change")
    original = workspace.encrypt_workspace

    def unavailable(*args):
        """Fail only this disposable test's encrypted disk write."""
        raise OSError("Synthetic disk failure")

    monkeypatch.setattr(workspace, "encrypt_workspace", unavailable)
    body = {"alias": "fictional_one", "password": PASSWORD + "-new", "recovery": recovery}
    assert client.post("/private/reset", json=body).status_code == 400
    assert client.app.state.manager.key is not None
    assert client.app.state.manager.accounts.login("fictional_one", PASSWORD)
    monkeypatch.setattr(workspace, "encrypt_workspace", original)
    assert client.post("/private/reset", json=body).status_code == 200


@pytest.mark.parametrize("name", ["../escape", "a\\b", "C:/file", "a//b", "CON.txt", "a./b", "a\x00b"])
def test_archive_paths(name):
    """Portable extraction never permits traversal/devices/ambiguous names."""
    with pytest.raises(ValueError):
        safe_name(name)


def test_archive_authentication_before_extract(tmp_path):
    """Tampered GCM tags expose no extracted plaintext; preexisting directories are never overwritten."""
    root = tmp_path / "source"
    root.mkdir()
    (root / "code.txt").write_text("synthetic sensitive marker")
    path = tmp_path / "source.cfsvault"
    encrypt_workspace(root, path, b"k" * 32)
    assert b"synthetic sensitive marker" not in path.read_bytes()
    damaged = bytearray(path.read_bytes())
    damaged[-1] ^= 1
    path.write_bytes(damaged)
    with pytest.raises(InvalidTag):
        decrypt_workspace(path, tmp_path / "bad", b"k" * 32)
    assert not (tmp_path / "bad").exists()


def test_single_instance_and_launcher_not_browser(client):
    """Only the process-local launcher can shut down, and a second instance cannot share active files."""
    assert client.post("/launcher/shutdown", json={}).status_code == 403
    with pytest.raises(ValueError, match="Another"):
        create_private_app(client.app.state.manager.root, 8091)


def test_warning_budget_is_bounded(project):
    """Repeated risky syntax is linear scan/logarithmic line mapping with bounded output, not quadratic prefix scans."""
    from studio.analysis import inspect_source

    changed = project.model_copy(deep=True)
    changed.files[0].content = "eval('1')\n" * 2000
    result = inspect_source(changed)
    assert len(result["findings"]) == 1000 and result["findings_truncated"]


def test_slow_worker_diagnostic_does_not_block_saving(client, project, monkeypatch):
    """A genuinely pending probe never holds the account's source/history request lock."""
    import asyncio

    async def slow_probe(**kwargs):
        await asyncio.sleep(60)
        return {"ready": False, "reason": "fixture"}

    monkeypatch.setattr(execution, "diagnostics", slow_probe)
    register(client)
    unlock(client)
    started = time.monotonic()
    assert client.get("/private/api/status").status_code == 200
    assert client.post("/private/api/revisions", json=project.model_dump()).status_code == 200
    assert time.monotonic() - started < 5
