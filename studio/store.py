# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Store@L33
# functions: __init__(self, path)@L36; connect(self)@L45; create(self, payload, parent)@L56; revision(self, identifier)@L83; history(self)@L96; queue(self, revision)@L106; finish(self, identifier, status, result)@L115; run(self, identifier)@L122; runs(self, revision)@L130; timeline(self, revision)@L141
# variables: SCHEMA@L23; connection@L40; connection@L47; revision@L58; connection@L59; previous@L61; old@L66; project@L73; project@L75; connection@L85; row@L86; connection@L98; row@L101; identifier@L108; connection@L109; connection@L117; connection@L124; row@L125; connection@L132; identifiers@L133; row@L135; identifier@L139; project@L143; connection@L144; rows@L145; items@L149; row@L150; payload@L151; attempts@L152; summaries@L156; attempt@L157; result@L158; key@L165
# parameters: path@L36; self@L36; self@L45; parent@L56; payload@L56; self@L56; identifier@L83; self@L83; self@L96; revision@L106; self@L106; identifier@L115; result@L115; self@L115; status@L115; identifier@L122; self@L122; revision@L130; self@L130; revision@L141; self@L141
# </code-map>

"""SQLite append-only project revisions and durable job evidence.

Symbol and variable locations: docs/code-index.md. Database connection lifetimes
are short; bound parameters and transactions prevent partial history updates.
"""

import hashlib
import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

SCHEMA = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, title TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS revisions(id TEXT PRIMARY KEY, project_id TEXT NOT NULL REFERENCES projects(id), parent_id TEXT REFERENCES revisions(id), payload TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, revision_id TEXT NOT NULL REFERENCES revisions(id), status TEXT NOT NULL, result TEXT NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX IF NOT EXISTS run_revision ON runs(revision_id);
CREATE INDEX IF NOT EXISTS revision_project ON revisions(project_id);
"""


class Store:
    """Own a local database; never place API keys or authentication tokens in history."""

    def __init__(self, path: Path):
        """Create the app-owned database and recover interrupted jobs as explicit failures."""
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)
            connection.execute("UPDATE runs SET status='interrupted' WHERE status IN ('queued','running')")

    @contextmanager
    def connect(self):
        """Bound one transactional connection with foreign keys and a busy timeout."""
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def create(self, payload: dict, parent: str | None = None) -> dict:
        """Append a revision; do not modify the parent or its approved test oracles."""
        revision = str(uuid4())
        with self.connect() as connection:
            if parent:
                previous = connection.execute(
                    "SELECT project_id,payload FROM revisions WHERE id=?", (parent,)
                ).fetchone()
                if not previous:
                    raise KeyError("Unknown parent")
                old = json.loads(previous["payload"])
                if old["cases"] != payload["cases"]:
                    raise ValueError("Candidate must retain the approved baseline oracles")
                if not payload["tests"].startswith(old["tests"]):
                    raise ValueError("Candidate must retain the approved baseline harness; append new tests")
                if old["language"] != payload["language"] or old["entry"] != payload["entry"]:
                    raise ValueError("Start a new baseline when changing language or entry")
                project = previous["project_id"]
            else:
                project = str(uuid4())
                connection.execute("INSERT INTO projects(id,title) VALUES(?,?)", (project, payload["title"]))
            connection.execute(
                "INSERT INTO revisions(id,project_id,parent_id,payload) VALUES(?,?,?,?)",
                (revision, project, parent, json.dumps(payload)),
            )
        return {"id": revision, "project_id": project, "parent_id": parent, "project": payload}

    def revision(self, identifier: str) -> dict:
        """Read a revision or raise without disclosing filesystem paths."""
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM revisions WHERE id=?", (identifier,)).fetchone()
        if not row:
            raise KeyError("Unknown revision")
        return {
            "id": row["id"],
            "project_id": row["project_id"],
            "parent_id": row["parent_id"],
            "project": json.loads(row["payload"]),
        }

    def history(self) -> list[dict]:
        """Return a bounded summary, excluding source bodies until explicitly opened."""
        with self.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT r.id,r.project_id,r.parent_id,r.created,p.title FROM revisions r JOIN projects p ON p.id=r.project_id ORDER BY r.rowid DESC LIMIT 200"
                )
            ]

    def queue(self, revision: str) -> str:
        """Persist a pending run before starting any asynchronous work."""
        identifier = str(uuid4())
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO runs VALUES(?,?,?, ?,CURRENT_TIMESTAMP)", (identifier, revision, "queued", "{}")
            )
        return identifier

    def finish(self, identifier: str, status: str, result: dict) -> None:
        """Atomically store a completed/blocked/interrupted run and its evidence."""
        with self.connect() as connection:
            connection.execute(
                "UPDATE runs SET status=?,result=? WHERE id=?", (status, json.dumps(result), identifier)
            )

    def run(self, identifier: str) -> dict:
        """Fetch evidence for one run with its exact source revision."""
        with self.connect() as connection:
            row = connection.execute("SELECT * FROM runs WHERE id=?", (identifier,)).fetchone()
        if not row:
            raise KeyError("Unknown run")
        return {**dict(row), "result": json.loads(row["result"])}

    def runs(self, revision: str) -> list[dict]:
        """List all attempts of a revision in stable insertion order."""
        with self.connect() as connection:
            identifiers = [
                row[0]
                for row in connection.execute(
                    "SELECT id FROM runs WHERE revision_id=? ORDER BY rowid", (revision,)
                )
            ]
        return [self.run(identifier) for identifier in identifiers]

    def timeline(self, revision: str) -> dict:
        """Export the latest 50 project revisions with bounded evidence summaries, not source/log bodies."""
        project = self.revision(revision)["project_id"]
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT id,parent_id,payload,created FROM revisions WHERE project_id=? ORDER BY rowid DESC LIMIT 51",
                (project,),
            ).fetchall()
            items = []
            for row in reversed(rows[:50]):
                payload = json.loads(row["payload"])
                attempts = connection.execute(
                    "SELECT id,status,result,created FROM runs WHERE revision_id=? ORDER BY rowid DESC LIMIT 10",
                    (row["id"],),
                ).fetchall()
                summaries = []
                for attempt in reversed(attempts):
                    result = json.loads(attempt["result"])
                    summaries.append(
                        {
                            "id": attempt["id"],
                            "status": attempt["status"],
                            "created": attempt["created"],
                            "checks": {
                                key: result.get("checks", {}).get(key) for key in ("passed", "failed")
                            },
                            "benchmark": result.get("benchmark", {}),
                            "coverage": result.get("coverage", {}),
                            "mutation_score": result.get("mutation", {}).get("score"),
                            "fuzz_status": result.get("fuzz", {}).get("status"),
                            "generated_tests_exit": result.get("generated_tests", {}).get("exit_code"),
                        }
                    )
                items.append(
                    {
                        "id": row["id"],
                        "parent_id": row["parent_id"],
                        "created": row["created"],
                        "snapshot_sha256": hashlib.sha256(row["payload"].encode()).hexdigest(),
                        "priorities": payload["priorities"],
                        "attempts": summaries,
                    }
                )
        return {
            "project_id": project,
            "revisions": items,
            "truncated": len(rows) > 50,
            "scope": "Latest 50 revisions; latest 10 attempts each. Full source/logs remain in their individual exports.",
        }
