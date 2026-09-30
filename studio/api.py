# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: create_app(data_directory, token, ui_directory, config)@L34; lifespan(app)@L47; guard(request, call_next)@L65; health()@L94; shutdown()@L99; status()@L108; capabilities()@L117; history()@L122; save(project, parent)@L127; revision(identifier)@L135; work(identifier, project)@L142; start(identifier)@L158; get_run(identifier)@L173; report(identifier, format)@L181; compare_runs(baseline, candidate)@L201; ai(request)@L216
# variables: store@L40; providers@L41; active@L42; semaphore@L43; ai_semaphore@L44; task@L50; app@L54; host@L67; origin@L68; permitted@L69; body@L78; chunk@L79; response@L84; callback@L101; result@L147; project@L163; job@L166; task@L167; result@L184; source@L185; new@L204; old@L204; new_revision@L205; old_revision@L205
# parameters: config@L35; data_directory@L35; token@L35; ui_directory@L35; app@L47; call_next@L65; request@L65; parent@L127; project@L127; identifier@L135; identifier@L142; project@L142; identifier@L158; identifier@L173; format@L181; identifier@L181; baseline@L201; candidate@L201; request@L216
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
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from studio import execution
from studio.analysis import compare
from studio.catalog import catalog
from studio.models import AIRequest, Project
from studio.providers import Providers
from studio.reports import bundle, html_report
from studio.store import Store


def create_app(
    data_directory: Path, token: str, ui_directory: Path | None = None, config: Path | None = None
) -> FastAPI:
    """Create one app instance; state and token are scoped to this app process."""
    if len(token) < 32:
        raise ValueError("Use a strong session token")
    store = Store(data_directory / "history.sqlite")
    providers = Providers(config)
    active: set[asyncio.Task] = set()
    semaphore = asyncio.Semaphore(2)
    ai_semaphore = asyncio.Semaphore(2)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Cancel broker-owned work on shutdown so containers are cleaned up."""
        yield
        for task in list(active):
            task.cancel()
        await asyncio.gather(*active, return_exceptions=True)

    app = FastAPI(
        title="Code Flow Studio",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.store = store

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
            "worker": await execution.diagnostics(),
            "providers": providers.public(),
            "active_jobs": len(active),
        }

    @app.get("/api/catalog")
    def capabilities():
        """List all 48 categories without implying any has been executed."""
        return catalog()

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
                result = await execution.run(project)
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
