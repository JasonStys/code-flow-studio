"""Shared CLI entry point for web launch and secret-free push analysis.

Symbol and variable locations: docs/code-index.md. Compiler execution always
uses the same container broker as the application; no permissive host fallback.
"""

import argparse
import asyncio
import json
import os
import secrets
from pathlib import Path

import uvicorn

from studio.api import create_app
from studio.execution import run
from studio.models import Project
from studio.reports import html_report


def main() -> None:
    """Launch the loopback UI or analyze a manifest into HTML/JSON CI evidence."""
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["serve", "analyze"])
    parser.add_argument("--port", type=int, default=8012)
    parser.add_argument("--data", type=Path, default=Path("runtime"))
    parser.add_argument("--ui", type=Path, default=Path("dist/ui"))
    parser.add_argument("--config", type=Path)
    parser.add_argument("--project", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    if args.mode == "serve":
        token = os.environ.get("STUDIO_TOKEN") or secrets.token_urlsafe(32)
        if not os.environ.get("STUDIO_TOKEN"):
            print(f"Open locally: http://127.0.0.1:{args.port}/#token={token}", flush=True)
        application = create_app(args.data, token, args.ui, args.config)
        server = uvicorn.Server(uvicorn.Config(application, host="127.0.0.1", port=args.port))
        application.state.shutdown = lambda: setattr(server, "should_exit", True)
        server.run()
    else:
        if not args.project:
            parser.error("--project required for analyze")
        project = Project.model_validate_json(args.project.read_text(encoding="utf-8"))
        result = asyncio.run(run(project))
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        (args.output / "report.html").write_text(html_report(result), encoding="utf-8")
        print(
            json.dumps(
                {
                    "tool_status": result["tool_status"],
                    "passed": result.get("checks", {}).get("passed", 0),
                    "failed": result.get("checks", {}).get("failed", 0),
                }
            )
        )
        failed = (
            result["tool_status"] != "completed"
            or result.get("checks", {}).get("failed", 0)
            or result.get("checks", {}).get("passed", 0) == 0
        )
        failed = (
            failed
            or result.get("generated_tests", {}).get("exit_code", 0) != 0
            or result.get("fuzz", {}).get("status") in {"findings", "blocked"}
            or bool(result.get("fuzz", {}).get("blocked_methods"))
        )
        raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
