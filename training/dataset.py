"""Rights-aware, group-disjoint training data preparation without executing examples.

Symbol and variable locations: docs/code-index.md. Each record requires provenance;
duplicate normalized prompts and whole projects stay within one split.
"""

import hashlib
import json
from pathlib import Path

LICENSES = {"owned", "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "CC0-1.0"}


def prepare(path: Path, seed: int = 42) -> tuple[list[dict], list[dict], dict]:
    """Validate bounded JSONL, deduplicate, and assign project groups to deterministic splits."""
    if path.stat().st_size > 16777216:
        raise ValueError("Dataset exceeds 16 MiB; shard and review it first")
    seen = {}
    groups: dict[str, list[dict]] = {}
    duplicates = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if set(row) != {"prompt", "completion", "project", "license"} or row["license"] not in LICENSES:
            raise ValueError("Each record needs prompt, completion, project, and an approved license")
        if not all(isinstance(value, str) and 0 < len(value) <= 16000 for value in row.values()):
            raise ValueError("Invalid or oversized record")
        key = hashlib.sha256(" ".join(row["prompt"].split()).encode()).hexdigest()
        if key in seen:
            if seen[key] != row["completion"]:
                raise ValueError("Conflicting completions for a duplicate prompt")
            duplicates += 1
            continue
        seen[key] = row["completion"]
        groups.setdefault(row["project"], []).append(row)
    if len(groups) < 2:
        raise ValueError("At least two independent project groups are required")
    ordered = sorted(groups, key=lambda group: hashlib.sha256(f"{seed}:{group}".encode()).hexdigest())
    validation_count = max(1, len(ordered) // 5)
    validation_projects = set(ordered[:validation_count])
    train = [row for group in ordered if group not in validation_projects for row in groups[group]]
    validation = [row for group in ordered if group in validation_projects for row in groups[group]]
    return (
        train,
        validation,
        {
            "train_records": len(train),
            "validation_records": len(validation),
            "project_disjoint": True,
            "duplicates_removed": duplicates,
            "seed": seed,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "licenses": sorted({row["license"] for row in train + validation}),
        },
    )
