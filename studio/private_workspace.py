# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: InstanceLock@L50; Workspaces@L78
# functions: atomic_json(path, value)@L37; __init__(self, path)@L53; close(self)@L73; __init__(self, root)@L81; archive(self, owner)@L116; status(self, owner, session)@L124; providers(self)@L136; unlock(self, owner, session, encoded, salt)@L150; require(self, owner, session)@L214; save(self, force)@L220; remove_active(self, owner)@L235; lock(self, owner)@L247; delete(self, owner)@L265; close(self)@L273
# variables: HISTORY_RECOVERY_BYTES@L34; descriptor@L39; name@L39; stream@L41; allowed@L87; p@L96; c@L119; config@L126; path@L138; data@L139; data@L143; k@L145; p@L145; v@L145; p@L148; key@L154; current@L155; config@L156; proof@L159; nonce@L170; config@L171; keys@L200; settings@L200; current@L228
# parameters: path@L37; value@L37; path@L53; self@L53; self@L73; root@L81; self@L81; owner@L116; self@L116; owner@L124; self@L124; session@L124; self@L136; encoded@L150; owner@L150; salt@L150; self@L150; session@L150; owner@L214; self@L214; session@L214; force@L220; self@L220; owner@L235; self@L235; owner@L247; self@L247; owner@L265; self@L265; self@L273
# </code-map>

"""Jason Stys: exclusive account-scoped controller, encrypted history/providers, and recoverable shutdown.

Locked archives do not protect active source/memory from the device's OS owner or administrator.
"""

import asyncio
import base64
import json
import os
import secrets
import shutil
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from starlette.concurrency import run_in_threadpool

from studio.accounts import Accounts, decode_field
from studio.api import create_app
from studio.permissions import protect_directory
from studio.providers import Providers
from studio.vault import AAD, decrypt_workspace, encrypt_workspace, members, signature

# Read recovery reserve exceeds the write stop, so a last in-flight job cannot lock out exports.
HISTORY_RECOVERY_BYTES = 160 * 1024**2


def atomic_json(path: Path, value: dict):
    """Atomically publish only a managed marker/config; retain the prior complete file on failure."""
    descriptor, name = tempfile.mkstemp(prefix=".publish-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(value, stream, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


class InstanceLock:
    """One process owns a dedicated account root; no second launcher may clean its active files."""

    def __init__(self, path: Path):
        """Hold a nonblocking OS advisory file lock until this controller closes."""
        self.stream = path.open("a+b")
        self.stream.seek(0)
        self.stream.write(b"1")
        self.stream.flush()
        self.stream.seek(0)
        try:
            if os.name == "nt":
                import msvcrt

                msvcrt.locking(self.stream.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl

                fcntl.flock(self.stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            self.stream.close()
            raise ValueError("Another application instance uses this account root; close it first") from None

    def close(self):
        """Release only this process's held descriptor."""
        self.stream.close()


class Workspaces:
    """One unlocked account engine, with separately vault-proven sessions and no admin read API."""

    def __init__(self, root: Path):
        """Protect a dedicated new root; leave old capstone/developer/desktop data untouched."""
        if root.is_symlink() or root.is_junction():
            raise ValueError("A private data root cannot be a link")
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True, mode=0o700)
        allowed = {
            "accounts.sqlite",
            "accounts.sqlite-wal",
            "accounts.sqlite-shm",
            "instance.lock",
            "active",
            "active-owner.json",
            "encrypted",
        }
        if any(p.name not in allowed for p in self.root.iterdir()):
            raise ValueError(
                "Choose an empty dedicated account directory; unrelated existing files were preserved"
            )
        protect_directory(self.root)
        self.instance = InstanceLock(self.root / "instance.lock")
        self.accounts = Accounts(self.root / "accounts.sqlite")
        self.active = self.root / "active"
        self.marker = self.root / "active-owner.json"
        self.archives = self.root / "encrypted"
        self.archives.mkdir(exist_ok=True, mode=0o700)
        self.owner = self.key = self.app = self.context = self.saved_signature = None
        self.sessions = set()
        self.token = secrets.token_urlsafe(32)
        self.requests = asyncio.Lock()
        self.failed = False
        if self.marker.exists() != self.active.exists():
            self.instance.close()
            raise ValueError("Incomplete recovery state; preserve this directory and seek support")

    def archive(self, owner: str) -> Path:
        """Use only server-generated opaque account IDs as encrypted archive names."""
        if not owner or any(
            c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_-" for c in owner
        ):
            raise ValueError("Invalid internal owner")
        return self.archives / (owner + ".cfsvault")

    def status(self, owner: str, session: str):
        """Never expose another owner's alias/history; require this session to prove its vault phrase."""
        config = self.accounts.vault(owner)["envelope"]
        return {
            "configured": bool(config),
            "salt": config["salt"] if config else None,
            "unlocked": self.owner == owner and session in self.sessions,
            "engine_busy": self.owner is not None and self.owner != owner,
            "recovery_pending": self.marker.exists() and self.owner is None,
            "save_failed": self.failed,
        }

    def providers(self) -> tuple[dict, dict]:
        """Read only this unlocked account's bounded settings; never export its API keys."""
        path = self.active / "providers.private.json"
        data = {"providers": [], "routes": {}}
        if path.exists():
            if path.stat().st_size > 128 * 1024:
                raise ValueError("Provider settings exceed their limit")
            data = json.loads(path.read_text(encoding="utf-8"))
        return {
            "providers": [{k: v for k, v in p.items() if k != "key"} for p in data["providers"]],
            "routes": data["routes"],
            "revision": data.get("revision", "unconfigured"),
        }, {p["id"]: p.get("key", "") for p in data["providers"]}

    async def unlock(self, owner: str, session: str, encoded: str, salt: str | None):
        """Authenticate the independent key, recover only its owner, then enter its genuine controller lifecycle."""
        if self.owner is not None and self.owner != owner:
            raise ValueError("Another account has this local engine unlocked; it must lock first")
        key = decode_field(encoded, 32, 32)
        current = self.accounts.vault(owner)
        config = current["envelope"]
        if config:
            try:
                proof = AESGCM(key).decrypt(
                    decode_field(config["iv"], 12, 12), decode_field(config["proof"], 16, 256), AAD
                )
                if proof != b"code-flow-local-key-v1":
                    raise ValueError()
            except Exception:
                raise ValueError("Cannot unlock: wrong vault phrase or damaged key settings") from None
        else:
            if self.marker.exists():
                raise ValueError("The interrupted account's owner must recover it first")
            decode_field(salt or "", 16, 16)
            nonce = secrets.token_bytes(12)
            config = {
                "salt": salt,
                "iv": base64.b64encode(nonce).decode(),
                "proof": base64.b64encode(
                    AESGCM(key).encrypt(nonce, b"code-flow-local-key-v1", AAD)
                ).decode(),
            }
            if not self.accounts.save(owner, config, current["revision"]):
                raise ValueError("Account changed; refresh")
        if self.owner == owner:
            self.sessions.add(session)
            return
        if self.marker.exists():
            if json.loads(self.marker.read_text())["owner"] != owner:
                raise ValueError("The interrupted account's owner must recover it first")
        else:
            if self.archive(owner).exists():
                try:
                    await run_in_threadpool(decrypt_workspace, self.archive(owner), self.active, key)
                except Exception:
                    raise ValueError("Cannot unlock damaged archive; existing files were preserved") from None
            else:
                self.active.mkdir(mode=0o700)
            atomic_json(self.marker, {"owner": owner})
        members(self.active)
        if (self.active / "history.sqlite").exists() and (
            self.active / "history.sqlite"
        ).stat().st_size > HISTORY_RECOVERY_BYTES:
            raise ValueError("History exceeds the recovery reserve; preserve this archive and seek support")
        settings, keys = self.providers()
        self.app = create_app(
            self.active,
            self.token,
            private_mode=True,
            owned_providers=Providers(settings=settings, credentials=keys),
        )
        self.context = self.app.router.lifespan_context(self.app)
        await self.context.__aenter__()
        self.owner, self.key = owner, key
        self.sessions = {session}
        self.saved_signature = None
        await run_in_threadpool(self.save, True)

    def require(self, owner: str, session: str):
        """A login cookie alone cannot join an already-unlocked account without key proof."""
        if self.owner != owner or session not in self.sessions or self.app is None:
            raise ValueError("Unlock this session's private workspace first")
        return self.app

    def save(self, force=False):
        """O(F) unchanged checks; O(S) streaming encryption only after idle data changes."""
        if self.owner is None:
            return {"saved": False}
        if self.app.state.active:
            if force:
                raise ValueError("Wait for compiler jobs before saving a complete snapshot")
            return {"saved": False, "pending": True}
        current = signature(self.active)
        if current != self.saved_signature:
            encrypt_workspace(self.active, self.archive(self.owner), self.key)
            self.saved_signature = current
        self.failed = False
        return {"saved": True}

    def remove_active(self, owner: str):
        """Delete only the exact managed working directory after validating its owner and resolved scope."""
        if (
            self.active.resolve() != self.root / "active"
            or self.active.is_symlink()
            or self.active.is_junction()
            or json.loads(self.marker.read_text())["owner"] != owner
        ):
            raise ValueError("Recovery ownership/path check failed")
        shutil.rmtree(self.active)
        self.marker.unlink()

    async def lock(self, owner: str):
        """Cancel/clean only this account's containers before sealing; preserve all recovery data on failure."""
        if self.owner != owner:
            return {"locked": True}
        try:
            if self.context:
                await self.context.__aexit__(None, None, None)
                self.context = None
                self.app.state.active.clear()
            await run_in_threadpool(self.save, True)
            await run_in_threadpool(self.remove_active, owner)
        except Exception:
            self.failed = True
            raise
        self.owner = self.key = self.app = self.saved_signature = None
        self.sessions.clear()
        return {"locked": True}

    async def delete(self, owner: str):
        """Current-password-authorized removal affects only this account, not another account's active engine."""
        if self.owner == owner:
            await self.lock(owner)
        elif self.marker.exists() and json.loads(self.marker.read_text())["owner"] == owner:
            await run_in_threadpool(self.remove_active, owner)
        self.archive(owner).unlink(missing_ok=True)

    async def close(self):
        """Attempt secure shutdown; failed snapshots remain recoverable rather than erased."""
        try:
            if self.owner:
                await self.lock(self.owner)
        finally:
            self.instance.close()
