# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_native_stage_is_opt_in_and_has_only_fixed_identity_fields(monkeypatch, capsys)@L22; test_native_stage_counts_are_only_nonnegative_integers(monkeypatch, capsys)@L37; test_actual_launcher_shutdown_denials_cannot_invoke_callback(tmp_path)@L48
# variables: payload@L29; prefix@L29; value@L31; value@L41; value@L44; app@L50; called@L51; headers@L53; client@L54; response@L61
# parameters: capsys@L22; monkeypatch@L22; capsys@L37; monkeypatch@L37; tmp_path@L48
# </code-map>

"""Jason Stys: opt-in native diagnostic privacy and genuine launcher acknowledgement.

Symbol locations: docs/code-index.md. Disposable accounts only; no host execution.
"""

import json

from fastapi.testclient import TestClient

from studio.native_lifecycle import native_stage
from studio.private_api import create_private_app


def test_native_stage_is_opt_in_and_has_only_fixed_identity_fields(monkeypatch, capsys):
    """Normal user operation emits no lifecycle diagnostics or private account information."""
    monkeypatch.delenv("STUDIO_DESKTOP_TEST", raising=False)
    native_stage("test-milestone")
    assert capsys.readouterr().out == ""
    monkeypatch.setenv("STUDIO_DESKTOP_TEST", "1")
    native_stage("test-milestone")
    prefix, payload = capsys.readouterr().out.strip().split(" ", 1)
    assert prefix == "NATIVE_SERVICE_STAGE"
    value = json.loads(payload)
    assert set(value) == {"stage", "pid", "parent_pid"}
    assert value["stage"] == "test-milestone"
    assert value["pid"] > 0 and value["parent_pid"] > 0


def test_native_stage_counts_are_only_nonnegative_integers(monkeypatch, capsys):
    """Fixed numeric drain observations never accept booleans, negative values or arbitrary strings."""
    monkeypatch.setenv("STUDIO_DESKTOP_TEST", "1")
    native_stage("http-drain-started", connections=2, tasks=0)
    value = json.loads(capsys.readouterr().out.strip().split(" ", 1)[1])
    assert value["connections"] == 2 and value["tasks"] == 0
    native_stage("http-drain-started", connections=True, tasks=-1)
    value = json.loads(capsys.readouterr().out.strip().split(" ", 1)[1])
    assert set(value) == {"stage", "pid", "parent_pid"}


def test_actual_launcher_shutdown_denials_cannot_invoke_callback(tmp_path):
    """Accepted shutdown means the real authenticated route actually invoked its graceful-stop callback."""
    app = create_private_app(tmp_path / "accounts", 8090, launcher_token="fictional-native-token")
    called = []
    app.state.shutdown = lambda: called.append(True)
    headers = {"X-CFS-Request": "v1", "Origin": "http://127.0.0.1:8090"}
    with TestClient(app, base_url="http://127.0.0.1:8090", headers=headers) as client:
        assert client.post("/launcher/shutdown", json={}).status_code == 403
        assert (
            client.post("/launcher/shutdown", json={}, headers={"Authorization": "Bearer wrong"}).status_code
            == 403
        )
        assert called == []
        response = client.post(
            "/launcher/shutdown", json={}, headers={"Authorization": "Bearer fictional-native-token"}
        )
        assert response.status_code == 200 and response.json() == {"stopping": True}
        assert called == [True]
