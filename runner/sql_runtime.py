# <code-map>
# Generated definition map; @L is the exact declaration line.
# Function/class docs explain behavior; variables/parameters are scoped inputs, outputs or state.
# functions: statements(text)@L22; main(entry)@L57
# variables: output@L24; start@L25; char@L26; index@L26; start@L30; item@L35; index@L37; source@L38; index@L41; end@L43; index@L44; end@L46; index@L47; item@L54; text@L59; chunks@L60; item@L61; lines@L61; output@L62; connection@L64; item@L65; row@L72
# parameters: text@L22; entry@L57
# </code-map>

"""Jason Stys: isolated SQLite statement runner with source anchors, not invented opcode-line coverage.

Executed via Python isolated mode; target-owned modules cannot replace this driver.
Definition/variable locations: docs/code-index.md. No SQLite extension loading is enabled.
"""

import json
import os
import sqlite3
import sys
from pathlib import Path


def statements(text: str) -> list[dict]:
    """Use SQLite's completeness parser; keep exact statement starts across quotes/comments/triggers."""
    output = []
    start = 0
    for index, char in enumerate(text):
        if char != ";" or not sqlite3.complete_statement(text[start:index + 1]):
            continue
        output.append({"text": text[start:index + 1], "offset": start})
        start = index + 1
        if len(output) > 4096:
            raise ValueError("SQL statement limit exceeded")
    if text[start:].strip():
        output.append({"text": text[start:], "offset": start})
    for item in output:
        # Remove only leading whitespace and SQL comments, never change the executed SQL.
        index = 0
        source = item["text"]
        while index < len(source):
            if source[index].isspace():
                index += 1
            elif source.startswith("--", index):
                end = source.find("\n", index)
                index = len(source) if end < 0 else end + 1
            elif source.startswith("/*", index):
                end = source.find("*/", index + 2)
                index = len(source) if end < 0 else end + 2
            else:
                break
        item["offset"] += index
        item["line"] = text.count("\n", 0, item["offset"]) + 1
        item["column"] = item["offset"] - text.rfind("\n", 0, item["offset"])
        item["empty"] = not source[index:].strip()
    return [item for item in output if not item["empty"]]


def main(entry: str) -> None:
    """Preserve executescript autocommit semantics; record completed top-level statement starts."""
    text = Path(entry).read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
    chunks = statements(text)
    lines = {str(item["line"]): 0 for item in chunks}
    output = os.environ.get("CFS_COVERAGE_OUTPUT")
    try:
        with sqlite3.connect(":memory:", isolation_level=None) as connection:
            for item in chunks:
                try:
                    connection.execute(item["text"])
                    lines[str(item["line"])] = 1
                except sqlite3.Error as error:
                    print(f"{entry}:{item['line']}:{item['column']}: SQLite statement-start anchor: {error}", file=sys.stderr)
                    raise SystemExit(1) from error
            for row in connection.execute(sys.stdin.read() or "SELECT 1"):
                print("|".join(map(str, row)))
    finally:
        if output:
            Path(output).write_text(json.dumps({entry: lines}), encoding="utf-8")


if __name__ == "__main__":
    main(sys.argv[1])
