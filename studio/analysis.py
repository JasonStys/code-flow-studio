# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: inspect_source(project)@L23; compare(baseline, candidate, priorities)@L93
# variables: file@L25; text@L25; lines@L26; findings@L27; truncated@L28; files@L29; patterns@L30; functions@L36; branches@L37; python_files@L38; file@L40; file@L45; used@L45; file@L46; digest@L49; located@L52; metadata@L52; functions@L55; branches@L56; content@L58; char@L59; index@L59; offsets@L59; message@L60; pattern@L60; match@L61; line@L64; previous@L65; truncated@L78; line@L83; reasons@L95; result@L96; dimensions@L117; area@L118; key@L118; metric@L118; after@L124; before@L124; metric@L127; total@L127; score@L128; metric@L129; value@L129
# parameters: project@L23; baseline@L93; candidate@L93; priorities@L93
# </code-map>

"""Non-executing source heuristics and cautious measured candidate comparisons.

Symbol and variable locations: docs/code-index.md. Heuristics are warnings,
not a security audit, semantic proof, or empirical Big-O measurement.
"""

import hashlib
import re
from bisect import bisect_right

from studio.models import Project
from studio.source_checks import python_checks, references


def inspect_source(project: Project) -> dict:
    """Measure source footprint; flag syntactic risk and readability proxies without importing code."""
    text = "\n".join(file.content for file in project.files if file.encoding == "text")
    lines = text.splitlines()
    findings = []
    truncated = False
    files = {}
    patterns = (
        (r"\beval\s*\(", "Dynamic evaluation"),
        (r"shell\s*=\s*True", "Shell execution"),
        (r"\bpickle\.loads?\s*\(", "Unsafe deserialization"),
        (r"(?i)(api[_-]?key|password|secret)\s*=\s*['\"][^'\"]{8,}", "Possible embedded secret"),
    )
    functions = 0
    branches = 0
    python_files = [
        file
        for file in project.files
        if file.encoding == "text"
        and project.language == "python"
        and (file.name.endswith(".py") or file.name == project.entry)
    ]
    used = references([file.content for file in python_files])
    for file in project.files:
        if file.encoding != "text":
            continue
        digest = hashlib.sha256(file.content.encode()).hexdigest()
        files[file.name] = {"source_sha256": digest}
        if file in python_files:
            located, metadata = python_checks(file.name, file.content, used)
            files[file.name].update(metadata)
            findings.extend(located[: max(0, 1001 - len(findings))])
            functions += metadata.get("function_count", 0)
            branches += metadata.get("branch_nodes", 0)
        else:
            content = file.content.replace("\r\n", "\n").replace("\r", "\n")
            offsets = [index for index, char in enumerate(content) if char == "\n"]
            for pattern, message in patterns:
                for match in re.finditer(pattern, content):
                    if len(findings) >= 1001:
                        break
                    line = bisect_right(offsets, match.start()) + 1
                    previous = offsets[line - 2] if line > 1 else -1
                    findings.append(
                        {
                            "file": file.name,
                            "line": line,
                            "column": match.start() - previous,
                            "source_sha256": digest,
                            "code": "TEXT-RISK",
                            "message": message,
                            "severity": "review",
                            "origin": "text-heuristic",
                        }
                    )
    truncated = len(findings) > 1000
    return {
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "source_bytes": len(text.encode()),
        "lines": len(lines),
        "long_lines": sum(len(line) > 110 for line in lines),
        "function_count": functions,
        "branch_nodes": branches,
        "findings": findings[:1000],
        "files": files,
        "findings_truncated": truncated,
        "caveat": "Python syntax and conservative unused/unreachable candidates; other text uses risk patterns only. Unused is not uncovered. No inferred Big-O, complete bug detection or security certification.",
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
