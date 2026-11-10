# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: require(condition, message)@L26; namespace(repository)@L32; release_id(value)@L42; identity(record, repository)@L48; read_by_id(read, repository, identifier)@L67; find_release(read, repository, tag, missing)@L86; require_draft(read, repository, version, source, expected_id)@L122
# variables: Reader@L20; PER_PAGE@L21; MAX_PAGES@L22; MAX_ID@L23; identifier@L51; tag@L52; target@L58; identifier@L69; record@L70; base@L88; matches@L94; seen@L95; page@L96; records@L97; record@L99; current@L100; candidate@L113; record@L114; record@L130
# parameters: condition@L26; message@L26; repository@L32; value@L42; record@L48; repository@L48; identifier@L67; read@L67; repository@L67; missing@L86; read@L86; repository@L86; tag@L86; expected_id@L123; read@L123; repository@L123; source@L123; version@L123
# </code-map>

"""Bounded authenticated draft lookup by Jason Stys.

Functions: namespace, release_id, identity, read_by_id, find_release, require_draft.
Variables: fixed page budget, unique tag and exact numeric identity; lines: docs/code-index.md.
No published-only tag lookup, permissive404 fallback or automatic mutation.
"""

import re
from collections.abc import Callable
from typing import Any

Reader = Callable[[str], Any]
PER_PAGE = 100
MAX_PAGES = 3
MAX_ID = 2**63 - 1


def require(condition: bool, message: str) -> None:
    """Fail closed even under optimized Python; no retry/fallback authorizes a write."""
    if not condition:
        raise ValueError(message)


def namespace(repository: str) -> str:
    """Namespace."""
    require(
        isinstance(repository, str)
        and re.fullmatch("[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository) is not None,
        "Invalid repository",
    )
    return f"repos/{repository}"


def release_id(value: Any) -> int:
    """Release id."""
    require(type(value) is int and 0 < value <= MAX_ID, "Invalid release ID")
    return value


def identity(record: Any, repository: str) -> tuple[Any, ...]:
    """Validate only documented immutable lookup fields; draft HTML URLs may use an untagged alias."""
    require(isinstance(record, dict), "Malformed release metadata")
    identifier = release_id(record.get("id"))
    tag = record.get("tag_name")
    require(isinstance(tag, str) and 0 < len(tag) <= 256, "Invalid release tag")
    require(
        type(record.get("draft")) is bool and type(record.get("prerelease")) is bool,
        "Invalid release state",
    )
    target = record.get("target_commitish")
    require(isinstance(target, str) and 0 < len(target) <= 256, "Invalid release target")
    require(
        record.get("url") == f"https://api.github.com/{namespace(repository)}/releases/{identifier}",
        "Foreign release URL",
    )
    return (identifier, tag, record["draft"], record["prerelease"], target)


def read_by_id(read: Reader, repository: str, identifier: int) -> dict[str, Any]:
    """Construct the same-repo numeric GET ourselves; never follow a returned URL or accept an ID swap."""
    identifier = release_id(identifier)
    record = read(f"{namespace(repository)}/releases/{identifier}")
    require(identity(record, repository)[0] == identifier, "Release ID changed")
    require(
        record.get("upload_url")
        == f"https://uploads.github.com/{namespace(repository)}/releases/{identifier}/assets{{?name,label}}",
        "Foreign upload URL",
    )
    require(
        record.get("assets_url")
        == f"https://api.github.com/{namespace(repository)}/releases/{identifier}/assets",
        "Foreign assets URL",
    )
    require(isinstance(record.get("assets"), list), "Malformed release assets")
    return record


def find_release(read: Reader, repository: str, tag: str, *, missing: bool = False) -> dict[str, Any] | None:
    """List all visible releases within a fixed cap, require a unique exact tag, then reread its ID."""
    base = namespace(repository)
    require(
        isinstance(tag, str)
        and re.fullmatch("v(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)", tag) is not None,
        "Invalid requested tag",
    )
    matches = []
    seen = set()
    for page in range(1, MAX_PAGES + 1):
        records = read(f"{base}/releases?per_page={PER_PAGE}&page={page}")
        require(isinstance(records, list) and len(records) <= PER_PAGE, "Malformed release page")
        for record in records:
            current = identity(record, repository)
            require(current[0] not in seen, "Duplicate release ID or unstable pagination")
            seen.add(current[0])
            if current[1] == tag:
                matches.append(record)
        if len(records) < PER_PAGE:
            break
    else:
        raise ValueError("Release history exceeds bounded complete lookup; absence not established")
    require(len(matches) <= 1, "Ambiguous release tag")
    if not matches:
        require(missing, "Release not found in complete authenticated listing")
        return None
    candidate = matches[0]
    record = read_by_id(read, repository, candidate["id"])
    require(
        identity(record, repository) == identity(candidate, repository),
        "Release identity changed between list and ID read",
    )
    return record


def require_draft(
    read: Reader, repository: str, version: str, source: str, *, expected_id: int | None = None
) -> dict[str, Any]:
    """Separate exact clean-source/draft policy from general collision detection during prepare."""
    require(
        isinstance(source, str) and re.fullmatch("[a-f0-9]{40}", source) is not None,
        "Invalid expected source",
    )
    record = find_release(read, repository, f"v{version}")
    require(record is not None, "Draft missing")
    require(
        record["draft"] is True and record["prerelease"] is False and (record["target_commitish"] == source),
        "Draft target/source/state mismatch",
    )
    if expected_id is not None:
        require(record["id"] == release_id(expected_id), "Prepared release ID changed")
    return record
