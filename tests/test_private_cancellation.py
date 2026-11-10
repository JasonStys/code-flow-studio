# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: test_cancelled_authorized_transition_is_completed_under_request_mutex(tmp_path, monkeypatch, kind)@L29; transition_scenario(tmp_path, monkeypatch, kind)@L34; stage(name)@L45; held_write()@L69; held_delete()@L81
# variables: base@L36; password@L37; key@L38; app@L39; manager@L40; entered@L41; release@L41; deferred@L42; original_stage@L43; request@L51; client@L55; owner@L60; archive@L61; config@L62; original@L67; request@L77; original@L79; request@L89; disk@L99; router@L100; name@L104; value@L104; row@L105; public@L108; restored@L111; db@L115
# parameters: kind@L29; monkeypatch@L29; tmp_path@L29; kind@L34; monkeypatch@L34; tmp_path@L34; name@L45; args@L69; args@L81
# </code-map>

"""Jason Stys: real authorized local mutations remain coherent after native request cancellation.

Symbol locations: docs/code-index.md. Only fictional accounts and inert provider
destinations are used; no provider API, worker, private account or external network.
"""

import asyncio
import base64
import json
import threading

import httpx
import pytest

from studio import completed_offload, private_api
from studio.private_api import create_private_app
from studio.vault import decrypt_workspace


@pytest.mark.parametrize("kind", ["providers", "delete"])
def test_cancelled_authorized_transition_is_completed_under_request_mutex(tmp_path, monkeypatch, kind):
    """Raw cancellation cannot split consent/destination publication or data/account deletion."""
    asyncio.run(transition_scenario(tmp_path, monkeypatch, kind))


async def transition_scenario(tmp_path, monkeypatch, kind):
    """Use actual route authorization and real disk/SQLite work with event-controlled cancellation."""
    base = "http://127.0.0.1:8090"
    password = "synthetic-transition-password-2026"
    key = b"k" * 32
    app = create_private_app(tmp_path / "accounts", 8090)
    manager = app.state.manager
    entered, release = threading.Event(), threading.Event()
    deferred = asyncio.Event()
    original_stage = completed_offload.native_stage

    def stage(name):
        """Wait for actual cancellation handling, rather than inferring it from elapsed time."""
        original_stage(name)
        deferred.set()

    monkeypatch.setattr(completed_offload, "native_stage", stage)
    request = None
    async with app.router.lifespan_context(app), httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url=base,
        headers={"Origin": base, "X-CFS-Request": "v1"}, trust_env=False,
    ) as client:
        assert (await client.post("/private/register", json={"alias": "fictional_transition", "password": password})).status_code == 200
        assert (await client.post("/private/unlock", json={
            "key": base64.b64encode(key).decode(), "salt": base64.b64encode(b"s" * 16).decode(),
        })).status_code == 200
        owner = manager.owner
        archive = manager.archive(owner)
        config = {
            "providers": [{"id": "owned", "kind": "openai", "url": "https://model.example/api", "model": "fixture", "key": "synthetic-provider-key-only"}],
            "routes": {"generate": "owned"},
        }
        if kind == "providers":
            original = private_api.atomic_json

            def held_write(*args):
                """Stop after the actual settings bytes changed but before the in-memory router can change."""
                original(*args)
                entered.set()
                if not release.wait(5):
                    raise AssertionError("Test did not release provider publication")

            monkeypatch.setattr(private_api, "atomic_json", held_write)
            request = asyncio.create_task(client.put("/private/providers", json=config))
        else:
            original = manager.accounts.delete

            def held_delete(*args):
                """Stop the actual final account-row removal after authorized workspace removal."""
                entered.set()
                if not release.wait(5):
                    raise AssertionError("Test did not release account deletion")
                return original(*args)

            monkeypatch.setattr(manager.accounts, "delete", held_delete)
            request = asyncio.create_task(client.post("/private/delete", json={"password": password, "confirm": True}))
        try:
            assert await asyncio.to_thread(entered.wait, 3)
            assert request.cancel()
            await asyncio.wait_for(deferred.wait(), 3)
            assert manager.requests.locked() and not request.done()
            release.set()
            with pytest.raises(asyncio.CancelledError):
                await request
            if kind == "providers":
                disk = json.loads((manager.active / "providers.private.json").read_text(encoding="utf-8"))
                router = manager.app.state.providers
                assert router.config["providers"][0]["url"] == disk["providers"][0]["url"] == config["providers"][0]["url"]
                assert router.config["routes"] == disk["routes"]
                assert router.config["providers"] == [
                    {name: value for name, value in row.items() if name != "key"}
                    for row in disk["providers"]
                ]
                assert router.credentials["owned"] == disk["providers"][0]["key"]
                public = await client.get("/private/providers")
                assert public.status_code == 200 and public.json()["revision"] == disk["revision"]
                assert config["providers"][0]["key"] not in public.text
                restored = tmp_path / "restored"
                decrypt_workspace(archive, restored, key)
                assert json.loads((restored / "providers.private.json").read_text()) == disk
            else:
                with manager.accounts.connection() as db:
                    assert db.execute("SELECT id FROM accounts WHERE id=?", (owner,)).fetchone() is None
                assert not archive.exists() and not manager.active.exists() and not manager.marker.exists()
        finally:
            release.set()
            if request and not request.done():
                with pytest.raises(asyncio.CancelledError):
                    await request
