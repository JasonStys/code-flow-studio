# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Boundary@L40; Closed@L140; Credentials@L146; Recovery@L153; Unlock@L159; Activity@L166; Delete@L172; Provider@L179; Settings@L192; Proxy@L226
# functions: __init__(self, app, manager, port)@L43; __call__(self, scope, receive, send)@L49; guarded(message)@L56; deny(status, detail)@L77; replay()@L129; coherent(self)@L201; public_settings(manager)@L213; __init__(self, manager)@L229; __call__(self, scope, receive, send)@L233; create_private_app(root, port, ui, launcher_token, nonce)@L284; lifespan(app)@L292; idle()@L295; invalid(request, error)@L331; bad_value(request, error)@L336; bad_disk(request, error)@L341; identify(request)@L347; signed(owner, data)@L351; auth_limit(alias)@L364; health()@L372; shutdown(request)@L383; register(data)@L396; login(data)@L406; reset(data)@L415; account(request)@L432; unlock(request, data)@L442; activity(request, data)@L453; save(request)@L461; lock(request)@L468; logout(request)@L476; delete(request, data)@L488; backup(request)@L504; get_providers(request)@L515; providers(request, data)@L522
# variables: CSP@L36; HISTORY_STOP_BYTES@L37; raw@L53; headers@L54; k@L54; v@L54; k@L61; v@L61; _@L83; k@L83; cookies@L101; token@L106; account@L107; chunks@L115; length@L115; message@L117; data@L120; length@L121; delivered@L127; delivered@L133; model_config@L143; alias@L149; password@L150; recovery@L156; key@L162; salt@L163; idle_seconds@L169; password@L175; confirm@L176; id@L182; kind@L183; url@L184; model@L185; key@L186; retain_key@L187; token_parameter@L188; temperature@L189; providers@L195; routes@L196; ids@L203; p@L203; value@L204; p@L207; keys@L215; settings@L215; data@L216; p@L218; manager@L237; app@L240; path@L245; db@L251; count@L252; headers@L264; forwarded@L273; k@L274; v@L274; manager@L288; task@L309; app@L319; response@L353; callback@L389; owner@L400; recovery@L400; owner@L409; db@L419; row@L420; fresh@L426; owner@L434; session@L434; owner@L444; session@L444; owner@L471; session@L471; owner@L479; session@L479; response@L483; _@L491; owner@L491; db@L492; row@L493; response@L499; _@L506; owner@L506; path@L507; keys@L526; old@L526; rows@L527; provider@L528; row@L529; p@L531; previous@L531; config@L536; router@L537; k@L539; p@L539; v@L539; p@L542
# parameters: app@L43; manager@L43; port@L43; self@L43; receive@L49; scope@L49; self@L49; send@L49; message@L56; detail@L77; status@L77; self@L201; manager@L213; manager@L229; self@L229; receive@L233; scope@L233; self@L233; send@L233; launcher_token@L285; nonce@L285; port@L285; root@L285; ui@L285; app@L292; error@L331; request@L331; error@L336; request@L336; error@L341; request@L341; request@L347; data@L351; owner@L351; alias@L364; request@L383; data@L396; data@L406; data@L415; request@L432; data@L442; request@L442; data@L453; request@L453; request@L461; request@L468; request@L476; data@L488; request@L488; request@L504; request@L515; data@L522; request@L522
# </code-map>

"""Jason Stys: loopback-only real accounts, session-proven vaults, private AI settings and scoped controller.

No public hosting, operator read backdoor, browser executable selection or permissive host execution.
"""

import asyncio
import contextlib
import secrets
import sqlite3
import time
from contextlib import asynccontextmanager
from http.cookies import CookieError, SimpleCookie
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, model_validator
from starlette.concurrency import run_in_threadpool

from studio.accounts import digest, password_matches
from studio.private_workspace import Workspaces, atomic_json
from studio.providers import Providers

CSP = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:; img-src 'self' data: blob:; connect-src 'self'; font-src 'self' data:; frame-src 'none'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'; form-action 'self'"
HISTORY_STOP_BYTES = 128 * 1024**2


class Boundary:
    """Validate one literal loopback origin before parsing; authenticate cookies only inside /private."""

    def __init__(self, app, manager: Workspaces, port: int):
        """Bind host/port and isolate cookie names from other local application instances."""
        self.app, self.manager, self.host = app, manager, f"127.0.0.1:{port}"
        self.cookie = f"cfs_account_{port}"
        manager.cookie = self.cookie

    async def __call__(self, scope, receive, send):
        """Bound request bytes and enforce Host, Origin, JSON/CSRF and private ownership before handlers."""
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        raw = scope["headers"]
        headers = {k.decode().lower(): v.decode() for k, v in raw}

        async def guarded(message):
            """Apply privacy/CSP headers even to denials and streamed downloads."""
            if message["type"] == "http.response.start":
                message["headers"] = [
                    (k, v)
                    for k, v in message["headers"]
                    if k.lower() not in {b"content-security-policy", b"cache-control", b"referrer-policy"}
                ]
                message["headers"] += [
                    (b"content-security-policy", CSP.encode()),
                    (b"cache-control", b"no-store"),
                    (b"referrer-policy", b"no-referrer"),
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (
                        b"permissions-policy",
                        b"camera=(),microphone=(),geolocation=(),payment=(),browsing-topics=()",
                    ),
                ]
            await send(message)

        async def deny(status, detail):
            """Errors are generic and never echo bodies, keys or local data paths."""
            await JSONResponse({"detail": detail}, status)(scope, receive, guarded)

        if (
            headers.get("host") != self.host
            or sum(k.lower() == b"host" for k, _ in raw) != 1
            or scope.get("scheme") != "http"
        ):
            return await deny(403, "Use this application's exact loopback address")
        if (
            headers.get("origin", "http://" + self.host) != "http://" + self.host
            or headers.get("sec-fetch-site") == "cross-site"
        ):
            return await deny(403, "Untrusted origin")
        if not await run_in_threadpool(
            self.manager.accounts.throttle, "request:" + str(scope.get("client", ("local",))[0]), 1000
        ):
            return await deny(429, "Too many requests; wait before retrying")
        if scope["method"] not in {"GET", "HEAD", "OPTIONS"} and (
            headers.get("x-cfs-request") != "v1"
            or headers.get("content-type", "").split(";")[0] != "application/json"
        ):
            return await deny(403, "Use the app's same-origin JSON request")
        cookies = SimpleCookie()
        try:
            cookies.load(headers.get("cookie", ""))
        except CookieError:
            return await deny(401, "Invalid session")
        token = cookies[self.cookie].value if self.cookie in cookies else ""
        account = await run_in_threadpool(self.manager.accounts.owner, token) if token else None
        scope.setdefault("state", {}).update(account=account, token=token, session=digest(token))
        if (
            scope["path"].startswith("/private/")
            and scope["path"] not in {"/private/login", "/private/register", "/private/reset"}
            and not account
        ):
            return await deny(401, "Sign in to your local account")
        chunks, length = [], 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            data = message.get("body", b"")
            length += len(data)
            if length > 4 * 1024**2:
                return await deny(413, "Request exceeds 4 MiB")
            chunks.append(data)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay():
            """Replay bounded bytes once and preserve normal disconnect/file streaming behavior."""
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": b"".join(chunks), "more_body": False}
            return await receive()

        await self.app(scope, replay, guarded)


class Closed(BaseModel):
    """Unknown fields never grant owner, filesystem or execution privileges."""

    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class Credentials(Closed):
    """Non-identifying lower-case alias; a long bounded login password."""

    alias: str = Field(pattern=r"^[a-z0-9_][a-z0-9_-]{2,39}$")
    password: str = Field(min_length=15, max_length=128)


class Recovery(Credentials):
    """One-use login recovery is independent of the irreversible vault phrase."""

    recovery: str = Field(min_length=32, max_length=128)


class Unlock(Closed):
    """Browser-derived key is used in the trusted service only while this account is unlocked."""

    key: str = Field(min_length=44, max_length=44)
    salt: str | None = Field(default=None, min_length=24, max_length=24)


class Activity(Closed):
    """Only intentional human activity renews idle timeout; passive polling does not."""

    idle_seconds: Literal[600, 1800, 7200] = 600


class Delete(Closed):
    """Current-password/explicit confirmation gates removal of this account only."""

    password: str = Field(min_length=15, max_length=128)
    confirm: Literal[True]


class Provider(Closed):
    """Explicitly chosen endpoint/model and own key; no global environment selectors or arbitrary tools."""

    id: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,39}$")
    kind: Literal["openai", "anthropic", "ollama"]
    url: str = Field(min_length=1, max_length=2048)
    model: str = Field(min_length=1, max_length=128)
    key: str = Field(default="", max_length=4096)
    retain_key: bool = False
    token_parameter: Literal["max_tokens", "max_completion_tokens"] = "max_tokens"  # noqa: S105 - protocol parameter, not a secret.
    temperature: float | None = Field(default=None, ge=0, le=2)


class Settings(Closed):
    """Up to eight closed provider records and explicit generate/tests/improve/suggest routes."""

    providers: list[Provider] = Field(default_factory=list, max_length=8)
    routes: dict[Literal["generate", "tests", "improve", "suggest"], str] = Field(
        default_factory=dict, max_length=4
    )

    @model_validator(mode="after")
    def coherent(self):
        """Reject duplicate/unknown IDs and invalid endpoint protocols before preserving any key."""
        ids = {p.id for p in self.providers}
        if len(ids) != len(self.providers) or any(value not in ids for value in self.routes.values()):
            raise ValueError("Choose unique provider IDs and existing task routes")
        Providers(
            settings={"providers": [p.model_dump() for p in self.providers], "routes": self.routes},
            credentials={},
        )
        return self


def public_settings(manager: Workspaces) -> dict:
    """Expose selected destinations/parameters and availability, never saved credentials."""
    settings, keys = manager.providers()
    data = {
        "providers": [
            {**p, "ready": bool(keys.get(p["id"])) or p["kind"] == "ollama"} for p in settings["providers"]
        ],
        "routes": settings["routes"],
    }
    data["revision"] = settings["revision"]
    return data


class Proxy:
    """Inject an internal bearer into the preserved controller only after session-specific key proof."""

    def __init__(self, manager: Workspaces):
        """Bind one exclusive, mutable account coordinator—not caller-selected filesystem roots."""
        self.manager = manager

    async def __call__(self, scope, receive, send):
        """Authorize every source/history/run/download/AI call; protect endpoint-consent version and history budgets."""
        if scope["type"] != "http":
            return
        manager = self.manager
        async with manager.requests:
            try:
                app = manager.require(scope["state"]["account"]["id"], scope["state"]["session"])
            except ValueError:
                return await JSONResponse({"detail": "Unlock this session's workspace first"}, 423)(
                    scope, receive, send
                )
            path = scope["path"].removeprefix("/private/api")
            if path == "/shutdown":
                return await JSONResponse({"detail": "Only the trusted launcher can stop the service"}, 403)(
                    scope, receive, send
                )
            if scope["method"] == "POST" and path == "/revisions":
                with app.state.store.connect() as db:
                    count = db.execute("SELECT count(*) FROM revisions").fetchone()[0]
                if count >= 500 or app.state.store.path.stat().st_size >= HISTORY_STOP_BYTES:
                    return await JSONResponse(
                        {"detail": "History capacity reached; export/backup before creating a new account"},
                        409,
                    )(scope, receive, send)
            if scope["method"] == "POST" and path.startswith("/revisions/") and path.endswith("/run"):
                if app.state.store.path.stat().st_size >= HISTORY_STOP_BYTES:
                    return await JSONResponse(
                        {"detail": "History capacity reached; reads and exports remain available"}, 409
                    )(scope, receive, send)
            if path == "/ai":
                headers = dict(scope["headers"])
                if (
                    headers.get(b"x-cfs-provider-revision", b"").decode()
                    != public_settings(manager)["revision"]
                ):
                    return await JSONResponse(
                        {"detail": "Provider settings changed; review destinations and renew source consent"},
                        409,
                    )(scope, receive, send)
            forwarded = dict(scope, path="/api" + path, root_path="")
            forwarded["headers"] = [(k, v) for k, v in scope["headers"] if k.lower() != b"authorization"] + [
                (b"authorization", ("Bearer " + manager.token).encode())
            ]
            await app(forwarded, receive, send)
            try:
                await run_in_threadpool(manager.save)
            except (OSError, ValueError):
                manager.failed = True


def create_private_app(
    root: Path, port: int, ui: Path | None = None, launcher_token: str = "", nonce: str = ""
):
    """Construct local account lifecycle; compiled jobs/AI remain explicit and private per-session."""
    manager = Workspaces(root)
    manager.last_human, manager.idle_seconds = time.monotonic(), 600

    @asynccontextmanager
    async def lifespan(app):
        """Bound idle snapshots and clean only owned jobs/workspaces on normal shutdown."""

        async def idle():
            """Background polling does not renew keys; snapshots wait for terminal jobs."""
            while True:
                await asyncio.sleep(5)
                async with manager.requests:
                    if manager.owner:
                        try:
                            if time.monotonic() - manager.last_human > manager.idle_seconds:
                                await manager.lock(manager.owner)
                            else:
                                await run_in_threadpool(manager.save)
                        except (OSError, ValueError, sqlite3.Error):
                            manager.failed = True

        task = asyncio.create_task(idle())
        try:
            yield
        finally:
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
            async with manager.requests:
                await manager.close()

    app = FastAPI(
        title="Code Flow Studio — Jason Stys",
        version="0.2.1",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.manager = manager
    app.add_middleware(Boundary, manager=manager, port=port)

    @app.exception_handler(RequestValidationError)
    async def invalid(request, error):
        """Never echo passwords, keys, source bodies or provider secrets from validation errors."""
        return JSONResponse({"detail": "Invalid fields; check the documented sizes/formats"}, 422)

    @app.exception_handler(ValueError)
    async def bad_value(request, error):
        """Return bounded authored errors, not arbitrary exception/SQL contents."""
        return JSONResponse({"detail": str(error)[:250]}, 400)

    @app.exception_handler(OSError)
    async def bad_disk(request, error):
        """A failed save preserves active recovery data and does not expose private paths."""
        return JSONResponse(
            {"detail": "Local storage operation failed; preserve recovery data and free disk space"}, 400
        )

    def identify(request):
        """Trust only the boundary's authenticated cookie identity, never body owner IDs."""
        return request.state.account["id"], request.state.session

    def signed(owner, data):
        """Issue a high-entropy HttpOnly local cookie; stored sessions contain only its digest."""
        response = JSONResponse(data)
        response.set_cookie(
            manager.cookie,
            manager.accounts.session(owner),
            httponly=True,
            samesite="strict",
            max_age=8 * 3600,
            path="/private",
        )
        return response

    async def auth_limit(alias):
        """Persist global/alias auth throttles without logging submitted secrets."""
        if not await run_in_threadpool(manager.accounts.throttle, "auth", 40) or not await run_in_threadpool(
            manager.accounts.throttle, "alias:" + alias, 10
        ):
            raise HTTPException(429, "Too many attempts; wait five minutes")

    @app.get("/health")
    def health():
        """Public ready metadata/launch correlation is not an authorization token."""
        return {
            "status": "ready",
            "mode": "private-local-accounts",
            "version": "0.2.1",
            "author": "Jason Stys",
            "launcher_nonce": nonce,
        }

    @app.post("/launcher/shutdown")
    def shutdown(request: Request):
        """Only an optional process-local native-launch secret can stop this service; never passed to the renderer."""
        if not launcher_token or not secrets.compare_digest(
            request.headers.get("authorization", ""), "Bearer " + launcher_token
        ):
            raise HTTPException(403, "Launcher authorization required")
        callback = getattr(app.state, "shutdown", None)
        if callback is None:
            raise HTTPException(409, "Launcher shutdown is unavailable")
        callback()
        return {"stopping": True}

    @app.post("/private/register")
    async def register(data: Credentials):
        """Create empty real accounts and show a random recovery code once, with no seeded/demo passwords."""
        await auth_limit(data.alias)
        try:
            owner, recovery = await run_in_threadpool(manager.accounts.register, data.alias, data.password)
        except sqlite3.IntegrityError:
            raise HTTPException(409, "Alias unavailable") from None
        return signed(owner, {"recovery": recovery})

    @app.post("/private/login")
    async def login(data: Credentials):
        """Authenticate a password without unlocking its independent source vault."""
        await auth_limit(data.alias)
        owner = await run_in_threadpool(manager.accounts.login, data.alias, data.password)
        if not owner:
            raise HTTPException(401, "Alias or password is incorrect")
        return signed(owner, {"signed_in": True})

    @app.post("/private/reset")
    async def reset(data: Recovery):
        """Seal before consuming a valid recovery code; storage failure must not lose the replacement code."""
        await auth_limit(data.alias)
        async with manager.requests:
            with manager.accounts.connection() as db:
                row = db.execute(
                    "SELECT id,recovery FROM accounts WHERE username=?", (data.alias,)
                ).fetchone()
            if not row or not secrets.compare_digest(row["recovery"], digest(data.recovery)):
                raise HTTPException(401, "Recovery credentials invalid")
            await manager.lock(row["id"])
            fresh = await run_in_threadpool(manager.accounts.reset, data.alias, data.recovery, data.password)
            if not fresh:
                raise HTTPException(409, "Recovery credentials changed")
            return {"recovery": fresh}

    @app.get("/private/account")
    def account(request: Request):
        """Return caller-only state; login-only sessions cannot see already-unlocked code."""
        owner, session = identify(request)
        return {
            "alias": request.state.account["username"],
            **manager.status(owner, session),
            "idle_seconds": manager.idle_seconds,
        }

    @app.post("/private/unlock")
    async def unlock(request: Request, data: Unlock):
        """Prove this session's key and intentionally reset the human-idle clock."""
        owner, session = identify(request)
        if not await run_in_threadpool(manager.accounts.throttle, "unlock:" + owner, 10):
            raise HTTPException(429, "Too many unlock attempts; wait five minutes")
        async with manager.requests:
            await manager.unlock(owner, session, data.key, data.salt)
            manager.last_human, manager.idle_seconds = time.monotonic(), 600
            return manager.status(owner, session)

    @app.post("/private/activity")
    async def activity(request: Request, data: Activity):
        """Only a vault-proven session can choose/renew human-idle timeout."""
        async with manager.requests:
            manager.require(*identify(request))
            manager.last_human, manager.idle_seconds = time.monotonic(), data.idle_seconds
            return {"idle_seconds": data.idle_seconds}

    @app.post("/private/save")
    async def save(request: Request):
        """Explicit complete encrypted backup requires no active compiler jobs."""
        async with manager.requests:
            manager.require(*identify(request))
            return await run_in_threadpool(manager.save, True)

    @app.post("/private/lock")
    async def lock(request: Request):
        """Cancel/clean this account's jobs, seal and drop active source/key; recovery stays on failure."""
        async with manager.requests:
            owner, session = identify(request)
            manager.require(owner, session)
            return await manager.lock(owner)

    @app.post("/private/logout")
    async def logout(request: Request):
        """Seal a proven account or revoke an unproven login; never cancel another account's jobs."""
        async with manager.requests:
            owner, session = identify(request)
            if manager.owner == owner and session in manager.sessions:
                await manager.lock(owner)
            await run_in_threadpool(manager.accounts.revoke, request.state.token)
        response = JSONResponse({"signed_out": True})
        response.delete_cookie(manager.cookie, path="/private")
        return response

    @app.post("/private/delete")
    async def delete(request: Request, data: Delete):
        """Require current password and confirmation; delete only this account and its live archive."""
        async with manager.requests:
            owner, _ = identify(request)
            with manager.accounts.connection() as db:
                row = db.execute("SELECT password FROM accounts WHERE id=?", (owner,)).fetchone()
            if not row or not await run_in_threadpool(password_matches, data.password, row[0]):
                raise HTTPException(401, "Current password incorrect")
            await manager.delete(owner)
            if not await run_in_threadpool(manager.accounts.delete, owner, data.password):
                raise HTTPException(409, "Account changed; sign in again")
        response = JSONResponse({"deleted": True})
        response.delete_cookie(manager.cookie, path="/private")
        return response

    @app.get("/private/backup")
    def backup(request: Request):
        """Download only this owner's encrypted archive; cold root backup also needs its account/key settings."""
        owner, _ = identify(request)
        path = manager.archive(owner)
        if not path.exists():
            raise HTTPException(404, "Save an encrypted snapshot first")
        return FileResponse(
            path, media_type="application/octet-stream", filename="code-flow-encrypted.cfsvault"
        )

    @app.get("/private/providers")
    async def get_providers(request: Request):
        """Return own endpoint choices/key availability; plaintext keys are never returned."""
        async with manager.requests:
            manager.require(*identify(request))
            return public_settings(manager)

    @app.put("/private/providers")
    async def providers(request: Request, data: Settings):
        """Store own explicit provider settings in the encrypted workspace, not environment/history/export bundles."""
        async with manager.requests:
            manager.require(*identify(request))
            old, keys = manager.providers()
            rows = []
            for provider in data.providers:
                row = provider.model_dump(exclude={"retain_key"})
                if provider.retain_key and not provider.key:
                    previous = next((p for p in old["providers"] if p["id"] == provider.id), None)
                    if not previous or (previous["url"], previous["kind"]) != (provider.url, provider.kind):
                        raise ValueError("Changed destination needs a newly entered key")
                    row["key"] = keys.get(provider.id, "")
                rows.append(row)
            config = {"providers": rows, "routes": data.routes, "revision": secrets.token_hex(16)}
            router = Providers(
                settings={
                    "providers": [{k: v for k, v in p.items() if k != "key"} for p in rows],
                    "routes": data.routes,
                },
                credentials={p["id"]: p["key"] for p in rows},
            )
            await run_in_threadpool(atomic_json, manager.active / "providers.private.json", config)
            manager.app.state.providers.config = router.config
            manager.app.state.providers.credentials = router.credentials
            await run_in_threadpool(manager.save)
            return public_settings(manager)

    app.mount("/private/api", Proxy(manager))
    if ui and ui.exists():
        app.mount("/", StaticFiles(directory=ui, html=True))
    return app
