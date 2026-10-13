# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: create_app(data_directory, token, ui_directory, config, private_mode, owned_providers)@L35; lifespan(app)@L53; probe()@L56; private_invalid(request, error)@L90; guard(request, call_next)@L95; health()@L124; shutdown()@L129; status()@L138; capabilities()@L147; review(project)@L152; history()@L157; save(project, parent)@L162; revision(identifier)@L170; work(identifier, project)@L177; start(identifier)@L197; get_run(identifier)@L212; report(identifier, format)@L220; compare_runs(baseline, candidate)@L241; ai(request)@L256
# variables: store@L46; providers@L47; active@L48; semaphore@L49; ai_semaphore@L50; checking@L62; owned@L66; task@L67; app@L71; host@L97; origin@L98; permitted@L99; body@L108; chunk@L109; response@L114; callback@L131; result@L182; project@L202; job@L205; task@L206; result@L223; source@L224; new@L244; old@L244; new_revision@L245; old_revision@L245
# parameters: data_directory@L36; token@L37; ui_directory@L38; config@L39; private_mode@L40; owned_providers@L41; app@L53; error@L90; request@L90; call_next@L95; request@L95; project@L152; parent@L162; project@L162; identifier@L170; identifier@L177; project@L177; identifier@L197; identifier@L212; format@L220; identifier@L220; baseline@L241; candidate@L241; request@L256
# </code-map>

"""Loopback-first authenticated API for web and native clients.

Symbol and variable locations: docs/code-index.md. Bounded jobs, constant-time
tokens, origin/host checks and immutable revisions constrain the local trust boundary.
"""

import asyncio
import json
import secrets
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from studio import execution
from studio.analysis import compare, inspect_source
from studio.catalog import catalog
from studio.models import AIRequest, Project
from studio.providers import Providers
from studio.reports import bundle, html_report
from studio.store import Store


def create_app(
    data_directory: Path,
    token: str,
    ui_directory: Path | None = None,
    config: Path | None = None,
    private_mode: bool = False,
    owned_providers: Providers | None = None,
) -> FastAPI:
    """Create one app instance; state and token are scoped to this app process."""
    if len(token) < 32:
        raise ValueError("Use a strong session token")
    store = Store(data_directory / "history.sqlite")
    providers = owned_providers or Providers(config)
    active: set[asyncio.Task] = set()
    semaphore = asyncio.Semaphore(2)
    ai_semaphore = asyncio.Semaphore(2)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Cancel broker-owned work on shutdown so containers are cleaned up."""

        async def probe():
            """Private readiness is cached, so a missing slow engine cannot hold the account request lock."""
            while True:
                app.state.worker_status = await execution.diagnostics(local_only=True)
                await asyncio.sleep(30)

        checking = asyncio.create_task(probe()) if private_mode else None
        try:
            yield
        finally:
            owned = list(active) + ([checking] if checking else [])
            for task in owned:
                task.cancel()
            await asyncio.gather(*owned, return_exceptions=True)

    app = FastAPI(
        title="Code Flow Studio",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.store = store
    app.state.active = active
    app.state.providers = providers
    app.state.worker_status = {
        "ready": False,
        "reason": "Checking local isolation; readiness refreshes every 30 seconds",
    }

    if private_mode:

        @app.exception_handler(RequestValidationError)
        async def private_invalid(request, error):
            """Private validation never reflects submitted code, embedded credentials or large fixtures."""
            return JSONResponse({"detail": "Invalid project/request fields; check documented formats"}, 422)

    @app.middleware("http")
    async def guard(request: Request, call_next):
        """Reject non-loopback hosts, cross-origin writes, oversized bodies, and invalid API tokens."""
        host = request.url.hostname
        origin = request.headers.get("origin")
        permitted = host in {"127.0.0.1", "localhost", "testserver"}
        if not permitted or (origin and origin != f"{request.url.scheme}://{request.url.netloc}"):
            return JSONResponse({"detail": "Host/origin rejected"}, status_code=403)
        if request.url.path.startswith("/api/") and not secrets.compare_digest(
            request.headers.get("authorization", ""), "Bearer " + token
        ):
            return JSONResponse({"detail": "Authentication required"}, status_code=401)
        # Read once to enforce the actual limit, including chunked bodies.
        if request.method in {"POST", "PUT", "PATCH"}:
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 1572864:
                    return JSONResponse({"detail": "Request too large"}, status_code=413)
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store" if request.url.path.startswith("/api/") else "no-cache"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; worker-src 'self' blob:; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'none'"
        )
        return response

    @app.get("/health")
    def health():
        """Return only readiness of the app, not execution or secret metadata."""
        return {"status": "ready", "version": "0.1.0"}

    @app.post("/api/shutdown")
    def shutdown():
        """Allow only the authenticated launcher to stop its own bundled service gracefully."""
        callback = getattr(app.state, "shutdown", None)
        if callback is None:
            raise HTTPException(409, "Shutdown is not configured for this app instance")
        callback()
        return {"status": "stopping"}

    @app.get("/api/status")
    async def status():
        """Show independent controller, worker and configured AI readiness."""
        return {
            "worker": app.state.worker_status if private_mode else await execution.diagnostics(),
            "providers": providers.public(),
            "active_jobs": len(active),
        }

    @app.get("/api/catalog")
    def capabilities():
        """List all 48 categories without implying any has been executed."""
        return catalog()

    @app.post("/api/review")
    def review(project: Project):
        """Return real non-executing syntax/footprint warnings, never pretend these are compiled tests."""
        return {"tool_status": "static-only", "static": inspect_source(project), "executed": False}

    @app.get("/api/revisions")
    def history():
        """Browse durable revision history."""
        return store.history()

    @app.post("/api/revisions")
    def save(project: Project, parent: str | None = None):
        """Save a source snapshot or approved candidate with immutable baseline cases."""
        try:
            return store.create(project.model_dump(), parent)
        except (KeyError, ValueError) as error:
            raise HTTPException(400, str(error)) from error

    @app.get("/api/revisions/{identifier}")
    def revision(identifier: str):
        """Retrieve the exact snapshot for editing or replay."""
        try:
            return {**store.revision(identifier), "runs": store.runs(identifier)}
        except KeyError as error:
            raise HTTPException(404, "Unknown revision") from error

    async def work(identifier: str, project: Project):
        """Execute bounded work asynchronously, with blocked and interrupted evidence retained."""
        try:
            async with semaphore:
                store.finish(identifier, "running", {})
                result = (
                    await execution.run(project, local_only=True, scratch=data_directory / "jobs")
                    if private_mode
                    else await execution.run(project)
                )
                store.finish(identifier, result["tool_status"], result)
        except asyncio.CancelledError:
            store.finish(identifier, "interrupted", {"reason": "Controller stopped"})
            raise
        except Exception:
            store.finish(
                identifier, "runner-error", {"reason": "Unexpected controller failure; see local diagnostics"}
            )

    @app.post("/api/revisions/{identifier}/run")
    async def start(identifier: str):
        """Queue at most four outstanding runs; reject unknown source revisions."""
        if len(active) >= 4:
            raise HTTPException(429, "Job queue full")
        try:
            project = Project.model_validate(store.revision(identifier)["project"])
        except KeyError as error:
            raise HTTPException(404, "Unknown revision") from error
        job = store.queue(identifier)
        task = asyncio.create_task(work(job, project))
        active.add(task)
        task.add_done_callback(active.discard)
        return {"id": job, "status": "queued"}

    @app.get("/api/runs/{identifier}")
    def get_run(identifier: str):
        """Return raw bounded tool evidence and target findings separately."""
        try:
            return store.run(identifier)
        except KeyError as error:
            raise HTTPException(404, "Unknown run") from error

    @app.get("/api/runs/{identifier}/report")
    def report(identifier: str, format: str = "html"):
        """Download inert HTML, JSON, or source/test/report ZIP artifacts."""
        try:
            result = store.run(identifier)
            source = store.revision(result["revision_id"])
            result["iteration_history"] = store.timeline(result["revision_id"])
        except KeyError as error:
            raise HTTPException(404, "Unknown run") from error
        if format == "zip":
            return Response(
                bundle(result, source),
                media_type="application/zip",
                headers={"Content-Disposition": 'attachment; filename="code-flow-evidence.zip"'},
            )
        if format == "json":
            return Response(json.dumps(result, indent=2), media_type="application/json")
        if format != "html":
            raise HTTPException(400, "Use html, json or zip")
        return Response(html_report(result), media_type="text/html")

    @app.get("/api/compare")
    def compare_runs(baseline: str, candidate: str):
        """Compare linked revisions only; retain independent baseline test requirements."""
        try:
            old, new = store.run(baseline), store.run(candidate)
            old_revision, new_revision = (
                store.revision(old["revision_id"]),
                store.revision(new["revision_id"]),
            )
        except KeyError as error:
            raise HTTPException(404, "Unknown run") from error
        if old_revision["project_id"] != new_revision["project_id"]:
            raise HTTPException(400, "Compare revisions of the same project")
        return compare(old["result"], new["result"], new_revision["project"]["priorities"])

    @app.post("/api/ai")
    async def ai(request: AIRequest):
        """Route one consented AI task; proposals never silently replace code or test oracles."""
        if ai_semaphore.locked():
            raise HTTPException(429, "AI request capacity reached")
        try:
            async with ai_semaphore:
                return await providers.request(request)
        except (ValueError, KeyError, TypeError) as error:
            raise HTTPException(400, str(error)[:300]) from error
        except Exception as error:
            raise HTTPException(502, "Provider failed or timed out; no code was changed") from error

    if ui_directory and ui_directory.exists():
        app.mount("/", StaticFiles(directory=ui_directory, html=True), name="ui")
    return app
