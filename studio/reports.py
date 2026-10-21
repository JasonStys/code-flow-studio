# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: location_summary(run)@L21; escape(value)@L26; html_report(run)@L106; bundle(run, revision)@L118
# variables: result@L23; findings@L24; rows@L30; value@L34; item@L43; coverage@L45; data@L67; name@L67; unknown@L69; item@L71; unknown@L73; data@L79; name@L79; key@L94; key@L97; evidence@L108; buffer@L120; archive@L121; file@L125
# parameters: run@L21; value@L26; run@L106; revision@L118; run@L118
# </code-map>

"""Portable machine-readable and escaped HTML evidence reports.

Symbol and variable locations: docs/code-index.md. All logs/source are plain
text in output; uploaded HTML is never rendered as trusted markup.
"""

import html
import io
import json
import zipfile


def location_summary(run: dict) -> str:
    """Render escaped location tables for both API envelopes and raw CLI results; retain legacy unknowns."""
    result = run.get("result", run)
    findings = result.get("static", {}).get("findings", []) + result.get("diagnostics", [])

    def escape(value) -> str:
        """Escape every label/message derived from source or tools, including malicious diagnostics."""
        return html.escape(str(value))

    rows = "".join(
        "<tr>"
        + "".join(
            "<td>" + escape(value) + "</td>"
            for value in (
                item.get("file", "Legacy: unavailable"),
                item.get("line", "Unavailable"),
                item.get("column") or "—",
                item.get("code", ""),
                item.get("message", ""),
            )
        )
        + "</tr>"
        for item in findings[:200]
    )
    coverage = "".join(
        "<h3>"
        + escape(name)
        + "</h3><p>"
        + (
            "Uncovered lines: "
            + escape(", ".join(map(str, data.get("missing_lines", []))) or "None recorded")
            + ". Missing branch arcs: "
            + escape(data.get("missing_branches", []))
            + ". Native branch points: "
            + escape(data.get("branch_points", []))
            + ". Measurement: "
            + escape(data.get("metric", "Python line/branch"))
            + (
                ". Truncated: an empty retained list is not full-coverage evidence."
                if data.get("truncated")
                else ""
            )
            if data.get("status") == "measured"
            else escape(data.get("reason", "Not measured"))
        )
        + "</p>"
        for name, data in result.get("coverage", {}).get("files", {}).items()
    )
    unknown = "".join(
        "<p>" + escape(item["stage"]) + ": " + escape(item["reason"]) + "</p>"
        for item in result.get("unlocated_failures", [])
    )
    unknown += "".join(
        "<p>"
        + escape(name)
        + ": parser stopped ("
        + escape(data.get("reason"))
        + "); exact line unavailable.</p>"
        for name, data in result.get("static", {}).get("files", {}).items()
        if data.get("parsed") is False and not data.get("location_available")
    )
    return (
        "<h2>Exact source locations</h2><p>Saved source snapshot, not unsaved editor text. Tool locations are not proven root causes; unused candidates are not uncovered lines. Up to 200 rows shown; raw evidence follows.</p>"
        + (
            "<table><tr><th>File</th><th>Line</th><th>Column</th><th>Code</th><th>Finding</th></tr>"
            + rows
            + "</table>"
            if rows
            else "<p>No located findings recorded; not proof of correctness.</p>"
        )
        + unknown
        + "<h2>Uncovered source locations</h2><p>Approved CLI reruns only; generated pytest excluded. Native branch IDs/counts are not destination arcs. Bash: command entry; SQL: completed statement starts; assembly: instruction-backed debug lines.</p>"
        + "<p>"
        + escape({key: result.get("coverage", {}).get(key) for key in ("status", "tool", "metric", "reason")})
        + "</p>"
        + "<p>Unused-code: "
        + escape({key: result.get("unused", {}).get(key) for key in ("status", "tool", "reason", "scope")})
        + "</p>"
        + (
            coverage
            or "<p>Exact missing lines unavailable/not measured in this report. Legacy totals cannot reconstruct line locations; rerun with the updated worker.</p>"
        )
    )


def html_report(run: dict) -> str:
    """Render a self-contained, script-free report preserving measured and blocked states."""
    evidence = html.escape(json.dumps(run, indent=2, ensure_ascii=False))
    return (
        '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Code Flow evidence</title><style>body{font:16px system-ui;max-width:1000px;margin:3rem auto;padding:1rem;color:#152238}td,th{padding:.5rem;text-align:left;overflow-wrap:anywhere}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f5fa;padding:1rem}</style><h1>Code Flow Studio · evidence report</h1><p>By Jason Stys. Tool completion is separate from target correctness. Missing checks are not passes. Review raw evidence and measurement caveats.</p>'
        + location_summary(run)
        + "<h2>Raw evidence</h2><pre>"
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
