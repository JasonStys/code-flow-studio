# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: ObservedServer@L121
# functions: test_actual_native_drain_preserves_authenticated_workspace(tmp_path, project, kind, monkeypatch)@L33; native_scenario(tmp_path, project, kind, monkeypatch)@L38; observe_offload(stage)@L56; held(request)@L65; held_save()@L79; held_decrypt()@L92; observed_app(scope, receive, send)@L104; observe_receive()@L110; startup(self, sockets)@L124; stage(self, name)@L129; test_private_cli_selects_finite_http_drain()@L234
# variables: listener@L40; port@L44; base@L45; token@L46; key@L47; app@L48; manager@L49; _@L50; budget@L50; entered@L50; ready@L50; release@L50; cancellation_deferred@L51; _@L52; thread_entered@L52; thread_finished@L52; thread_release@L52; counts@L53; events@L53; original_stage@L54; original_save@L76; original_decrypt@L77; result@L86; result@L98; partial@L108; message@L114; partial@L116; server@L137; running@L139; pending@L140; writer@L141; client@L147; response@L148; response@L152; response@L156; owner@L158; revision@L158; archive@L159; _@L161; writer@L161; cookie@L162; name@L162; value@L162; pending@L173; pending@L179; pending@L182; response@L185; response@L199; _@L205; name@L205; tasks@L205; restored@L213; config@L237
# parameters: kind@L33; monkeypatch@L33; project@L33; tmp_path@L33; kind@L38; monkeypatch@L38; project@L38; tmp_path@L38; stage@L56; request@L65; args@L79; args@L92; receive@L104; scope@L104; send@L104; self@L124; sockets@L124; name@L129; self@L129
# </code-map>

"""Jason Stys: real owned-loopback HTTP cancellation, authenticated accounts and vault recovery.

Symbol locations: docs/code-index.md. These disposable tests never execute code,
use Docker, connect user accounts or replace installed applications.
"""

import asyncio
import base64
import contextlib
import socket
import threading

import httpx
import pytest
from fastapi import Request

from studio import completed_offload, private_workspace
from studio.native_server import HTTP_DRAIN_SECONDS, NativeServer, native_config
from studio.private_api import create_private_app
from studio.vault import decrypt_workspace


@pytest.mark.parametrize("kind", ["locked-handler", "partial-upload", "offloaded-save", "offloaded-unlock"])
def test_actual_native_drain_preserves_authenticated_workspace(tmp_path, project, kind, monkeypatch):
    """Finite real HTTP drain cancels held work; cancellation cleanup finishes before authenticated sealing."""
    asyncio.run(native_scenario(tmp_path, project, kind, monkeypatch))


async def native_scenario(tmp_path, project, kind, monkeypatch):
    """Own one socket/server, create a real synthetic account and recover its exact stored revision."""
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind(("127.0.0.1", 0))
    listener.listen(128)
    listener.setblocking(False)
    port = listener.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    token = "fictional-native-drain-launch-secret"
    key = b"k" * 32
    app = create_private_app(tmp_path / "accounts", port, launcher_token=token)
    manager = app.state.manager
    entered, release, ready, budget = (asyncio.Event() for _ in range(4))
    cancellation_deferred = asyncio.Event()
    thread_entered, thread_release, thread_finished = (threading.Event() for _ in range(3))
    events, counts = [], []
    original_stage = completed_offload.native_stage

    def observe_offload(stage):
        """Signal only after genuine outer-task cancellation reached the protected offload."""
        original_stage(stage)
        if stage == "offload-cancellation-deferred":
            cancellation_deferred.set()

    monkeypatch.setattr(completed_offload, "native_stage", observe_offload)

    @app.get("/private/synthetic-held")
    async def held(request: Request):
        """Use the actual authenticated boundary and request mutex before a test-controlled suspension."""
        async with manager.requests:
            manager.require(request.state.account["id"], request.state.session)
            entered.set()
            try:
                await release.wait()
            finally:
                events.append("request-lock-released")
        return {"released": True}

    original_save = manager.save
    original_decrypt = private_workspace.decrypt_workspace

    def held_save(*args):
        """Hold a genuine snapshot offload until the actual cancellation stage has been observed."""
        thread_entered.set()
        try:
            if not thread_release.wait(15):
                raise AssertionError("Test did not release its own snapshot worker")
            assert manager.active.is_dir() and manager.owner is not None
            result = original_save(*args)
            events.append("snapshot-worker-finished")
            return result
        finally:
            thread_finished.set()

    def held_decrypt(*args):
        """Hold actual authenticated restore, then allow its marker/controller/key transition to finish."""
        thread_entered.set()
        try:
            if not thread_release.wait(15):
                raise AssertionError("Test did not release its own restore worker")
            result = original_decrypt(*args)
            events.append("restore-worker-finished")
            return result
        finally:
            thread_finished.set()

    async def observed_app(scope, receive, send):
        """Observe a real partial HTTP body without replacing the actual request/security handler."""
        if scope["type"] != "http" or scope["path"] != "/private/activity":
            return await app(scope, receive, send)
        partial = False

        async def observe_receive():
            nonlocal partial
            if partial:
                entered.set()
            message = await receive()
            if message["type"] == "http.request" and message.get("more_body"):
                partial = True
            return message

        return await app(scope, observe_receive, send)

    class ObservedServer(NativeServer):
        """Observe actual Uvicorn startup/drain rather than substituting fake service readiness."""

        async def startup(self, sockets=None):
            """A ready event follows the real listener/lifespan startup."""
            await super().startup(sockets)
            ready.set()

        def stage(self, name):
            """Retain actual numeric work counts and signal the real configured drain deadline."""
            super().stage(name)
            events.append(name)
            counts.append((name, len(self.server_state.connections), len(self.server_state.tasks)))
            if name == "http-drain-budget-exhausted":
                budget.set()

    server = ObservedServer(native_config(observed_app, port))
    app.state.shutdown = lambda: setattr(server, "should_exit", True)
    running = asyncio.create_task(server.serve(sockets=[listener]))
    pending = None
    writer = None
    try:
        await asyncio.wait_for(ready.wait(), 10)
        async with httpx.AsyncClient(
            base_url=base, headers={"Origin": base, "X-CFS-Request": "v1"},
            timeout=15, trust_env=False,
        ) as client:
            response = await client.post("/private/register", json={
                "alias": "fictional_drain", "password": "synthetic-drain-password-only-2026",
            })
            assert response.status_code == 200
            response = await client.post("/private/unlock", json={
                "key": base64.b64encode(key).decode(), "salt": base64.b64encode(b"s" * 16).decode(),
            })
            assert response.status_code == 200
            response = await client.post("/private/api/revisions", json=project.model_dump())
            assert response.status_code == 200
            revision, owner = response.json()["id"], manager.owner
            archive = manager.archive(owner)
            if kind == "partial-upload":
                _, writer = await asyncio.open_connection("127.0.0.1", port)
                cookie = "; ".join(f"{name}={value}" for name, value in client.cookies.items())
                writer.write((
                    f"POST /private/activity HTTP/1.1\r\nHost: 127.0.0.1:{port}\r\n"
                    f"Origin: {base}\r\nCookie: {cookie}\r\nX-CFS-Request: v1\r\n"
                    "Content-Type: application/json\r\nContent-Length: 30\r\n\r\n{"
                ).encode())
                await writer.drain()
            elif kind == "offloaded-unlock":
                assert (await client.post("/private/lock", json={})).status_code == 200
                assert not manager.active.exists() and manager.owner is None
                monkeypatch.setattr(private_workspace, "decrypt_workspace", held_decrypt)
                pending = asyncio.create_task(client.post("/private/unlock", json={
                    "key": base64.b64encode(key).decode(), "salt": base64.b64encode(b"s" * 16).decode(),
                }))
                assert await asyncio.to_thread(thread_entered.wait, 10)
            elif kind == "offloaded-save":
                manager.save = held_save
                pending = asyncio.create_task(client.post("/private/save", json={}))
                assert await asyncio.to_thread(thread_entered.wait, 10)
            else:
                pending = asyncio.create_task(client.get("/private/synthetic-held"))
            if kind not in {"offloaded-save", "offloaded-unlock"}:
                await asyncio.wait_for(entered.wait(), 10)
            response = await client.post("/launcher/shutdown", json={}, headers={"Authorization": "Bearer " + token})
            assert response.status_code == 200 and response.json() == {"stopping": True}
            await asyncio.wait_for(budget.wait(), 10)
            if kind in {"offloaded-save", "offloaded-unlock"}:
                # The original raw asyncio cancellation released this mutex while
                # the real snapshot worker was still using active plaintext files.
                await asyncio.wait_for(cancellation_deferred.wait(), 5)
                assert manager.requests.locked()
                assert kind != "offloaded-save" or manager.active.is_dir()
                assert not thread_finished.is_set() and not running.done()
                thread_release.set()
            await asyncio.wait_for(asyncio.shield(running), 10)
            if pending:
                try:
                    response = await asyncio.wait_for(pending, 5)
                    assert response.status_code == 500
                except httpx.RemoteProtocolError:
                    # Cancellation may close the HTTP connection without a response;
                    # a successful response is never accepted for the canceled action.
                    pass
            assert any(name == "http-drain-budget-exhausted" and tasks >= 1 for name, _, tasks in counts)
            assert events.index("http-request-cleanup-complete") < events.index("http-drain-complete")
            if kind == "offloaded-save":
                assert events.index("snapshot-worker-finished") < events.index("http-request-cleanup-complete")
            if kind == "offloaded-unlock":
                assert events.index("restore-worker-finished") < events.index("http-request-cleanup-complete")
            assert not manager.active.exists() and not manager.marker.exists()
            assert manager.owner is None and manager.key is None
            restored = tmp_path / "restored"
            decrypt_workspace(archive, restored, key)
            from studio.store import Store
            assert Store(restored / "history.sqlite").revision(revision)["project"] == project.model_dump()
    finally:
        release.set()
        thread_release.set()
        manager.save = original_save
        if writer:
            writer.close()
            await writer.wait_closed()
        server.should_exit = True
        if not running.done():
            await asyncio.wait_for(asyncio.shield(running), 20)
        if pending and not pending.done():
            pending.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pending
        listener.close()


def test_private_cli_selects_finite_http_drain():
    """The shipping configuration retains network/concurrency limits and finite HTTP drain."""
    assert HTTP_DRAIN_SECONDS == 5.0
    config = native_config(None, 8090)
    assert config.timeout_graceful_shutdown == HTTP_DRAIN_SECONDS
    assert config.host == "127.0.0.1" and config.port == 8090
    assert config.proxy_headers is False and config.limit_concurrency == 50
