# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# classes: Store@L32
# functions: __init__(self, path)@L35; connect(self)@L44; create(self, payload, parent)@L55; revision(self, identifier)@L82; history(self)@L95; queue(self, revision)@L105; finish(self, identifier, status, result)@L114; run(self, identifier)@L121; runs(self, revision)@L129
# variables: SCHEMA@L22; connection@L39; connection@L46; revision@L57; connection@L58; previous@L60; old@L65; project@L72; project@L74; connection@L84; row@L85; connection@L97; row@L100; identifier@L107; connection@L108; connection@L116; connection@L123; row@L124; connection@L131; identifiers@L132; row@L134; identifier@L138
# parameters: path@L35; self@L35; self@L44; parent@L55; payload@L55; self@L55; identifier@L82; self@L82; self@L95; revision@L105; self@L105; identifier@L114; result@L114; self@L114; status@L114; identifier@L121; self@L121; revision@L129; self@L129
# </code-map>

"""SQLite append-only project revisions and durable job evidence.

Symbol and variable locations: docs/code-index.md. Database connection lifetimes
are short; bound parameters and transactions prevent partial history updates.
"""

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
