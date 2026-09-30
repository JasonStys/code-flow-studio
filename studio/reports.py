"""Portable machine-readable and escaped HTML evidence reports.

Symbol and variable locations: docs/code-index.md. All logs/source are plain
text in output; uploaded HTML is never rendered as trusted markup.
"""

import html
import io
import json
import zipfile


def html_report(run: dict) -> str:
    """Render a self-contained, script-free report preserving measured and blocked states."""
    evidence = html.escape(json.dumps(run, indent=2, ensure_ascii=False))
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Code Flow evidence</title><style>body{font:16px system-ui;max-width:1000px;margin:3rem auto;padding:1rem;color:#152238}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5fa;padding:1rem}</style><h1>Code Flow Studio · evidence report</h1><p>Tool completion is separate from target correctness. Missing checks are not passes. Review raw evidence and measurement caveats.</p><pre>'
        + evidence
        + "</pre></html>"
    )


def bundle(run: dict, revision: dict) -> bytes:
    """Export source snapshot, tests, manifest and reports as inert downloadable artifacts."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("report.json", json.dumps(run, indent=2))
        archive.writestr("report.html", html_report(run))
        archive.writestr("project.json", json.dumps(revision["project"], indent=2))
        for file in revision["project"]["files"]:
            from studio.models import SourceFile

            archive.writestr("source/" + file["name"], SourceFile.model_validate(file).bytes())
        archive.writestr("generated/test_generated.py", revision["project"]["tests"])
        archive.writestr("generated/fuzz_harness.txt", revision["project"]["fuzz_harness"])
    return buffer.getvalue()
