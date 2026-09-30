# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: inspect_source(project)@L22; compare(baseline, candidate, priorities)@L63
# variables: file@L24; text@L24; lines@L25; findings@L26; patterns@L27; message@L33; pattern@L33; match@L34; functions@L38; branches@L39; file@L42; tree@L42; functions@L43; node@L44; branches@L46; node@L47; line@L55; reasons@L65; result@L66; dimensions@L87; area@L88; key@L88; metric@L88; after@L94; before@L94; metric@L97; total@L97; score@L98; metric@L99; value@L99
# parameters: project@L22; baseline@L63; candidate@L63; priorities@L63
# </code-map>

"""Non-executing source heuristics and cautious measured candidate comparisons.

Symbol and variable locations: docs/code-index.md. Heuristics are warnings,
not a security audit, semantic proof, or empirical Big-O measurement.
"""

import ast
import hashlib
import re

from studio.models import Project


def inspect_source(project: Project) -> dict:
    """Measure source footprint; flag syntactic risk and readability proxies without importing code."""
    text = "\n".join(file.content for file in project.files if file.encoding == "text")
    lines = text.splitlines()
    findings = []
    patterns = (
        (r"\beval\s*\(", "Dynamic evaluation"),
        (r"shell\s*=\s*True", "Shell execution"),
        (r"\bpickle\.loads?\s*\(", "Unsafe deserialization"),
        (r"(?i)(api[_-]?key|password|secret)\s*=\s*['\"][^'\"]{8,}", "Possible embedded secret"),
    )
    for pattern, message in patterns:
        for match in re.finditer(pattern, text):
            findings.append(
                {"line": text.count("\n", 0, match.start()) + 1, "message": message, "severity": "review"}
            )
    functions = 0
    branches = 0
    if project.language == "python":
        try:
            tree = ast.parse(next(file.content for file in project.files if file.name == project.entry))
            functions = sum(
                isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) for node in ast.walk(tree)
            )
            branches = sum(
                isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.Match)) for node in ast.walk(tree)
            )
        except SyntaxError as error:
            findings.append({"line": error.lineno, "message": "Python syntax error", "severity": "error"})
    return {
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_bytes": len(text.encode()),
        "lines": len(lines),
        "long_lines": sum(len(line) > 110 for line in lines),
        "function_count": functions,
        "branch_nodes": branches,
        "findings": findings,
        "caveat": "Readability/complexity proxies only. No inferred Big-O or security certification.",
    }


def compare(baseline: dict, candidate: dict, priorities: dict) -> dict:
    """Gate ranking on passing independent oracles and matching benchmark conditions."""
    reasons = []
    for result in (baseline, candidate):
        if (
            result.get("checks", {}).get("failed", 0)
            or result.get("checks", {}).get("passed", 0) == 0
            or result.get("tool_status") != "completed"
        ):
            reasons.append("Both versions need completed execution and passing approved cases")
        if result.get("generated_tests", {}).get("exit_code", 0) != 0:
            reasons.append("A generated/baseline harness failed")
        if result.get("fuzz", {}).get("status") in {"findings", "blocked"} or result.get("fuzz", {}).get(
            "blocked_methods"
        ):
            reasons.append("Fuzz findings or selected blocked methods need review")
    if baseline.get("oracle_hash") != candidate.get("oracle_hash"):
        reasons.append("Approved oracles differ")
    if baseline.get("environment") != candidate.get("environment"):
        reasons.append("Benchmark environments differ")
    if candidate.get("static", {}).get("findings") and priorities.get("scrutiny") == "strict":
        reasons.append("Strict review requires resolving candidate static warnings")
    if reasons:
        return {"eligible": False, "reasons": sorted(set(reasons)), "score": None}
    dimensions = {}
    for metric, area, key in (
        ("runtime", "benchmark", "median_ms"),
        ("memory", "benchmark", "max_rss_kib"),
        ("readability", "static", "long_lines"),
        ("footprint", "static", "source_bytes"),
    ):
        before, after = baseline.get(area, {}).get(key), candidate.get(area, {}).get(key)
        if isinstance(before, (int, float)) and isinstance(after, (int, float)):
            dimensions[metric] = max(-1, min(1, (before - after) / max(before, 1)))
    total = sum(priorities.get(metric, 0) for metric in dimensions)
    score = (
        sum(priorities.get(metric, 0) * value for metric, value in dimensions.items()) / total
        if total
        else None
    )
    return {
        "eligible": True,
        "reasons": [],
        "score": score,
        "relative_changes": dimensions,
        "caveat": "Process-level timing/RSS includes startup; small deltas may be noise. Readability is a long-line proxy. Human review still required.",
    }
